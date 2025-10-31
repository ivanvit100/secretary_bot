import os
import json
import telebot
import logging
import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from telebot import types
from libs.plots import *
from i18n import _

current_dir = os.path.dirname(os.path.abspath(__file__))
balance_file_path = os.path.join(current_dir, '../data/balance.json')

def balance_main(message: telebot.types.Message, bot: telebot.TeleBot):
    message_parts = message.text.split(' ')
    if len(message_parts) == 1:
        data = get_full_balance()
        mounth_plot(data)
        current_balance, current_saldo = get_balance()
        month = datetime.datetime.now().strftime('%B')
        caption = _('balance_current_month', month=month, balance=current_balance, saldo=current_saldo)
        with open('mounth_plot.png', 'rb') as photo:
            bot.send_photo(message.from_user.id, photo, caption=caption, parse_mode='Markdown')
        os.remove('mounth_plot.png')
    else:
        try:
            new_balance = float(message_parts[1])
            if new_balance < 0:
                update_balance(new_balance, 'uncategorized')
                
                markup = types.InlineKeyboardMarkup(row_width=3)
                markup.add(
                    types.InlineKeyboardButton(_("expense_important"), callback_data=f"expense_cat_important_{abs(new_balance)}"),
                    types.InlineKeyboardButton(_("expense_unplanned"), callback_data=f"expense_cat_unplanned_{abs(new_balance)}"),
                    types.InlineKeyboardButton(_("expense_repetable"), callback_data=f"expense_cat_repetable_{abs(new_balance)}")
                )
                markup.add(
                    types.InlineKeyboardButton(_("expense_optional"), callback_data=f"expense_cat_optional_{abs(new_balance)}"),
                    types.InlineKeyboardButton(_("expense_uncategorized"), callback_data=f"expense_cat_uncategorized_{abs(new_balance)}")
                )
                
                bot.send_message(
                    message.from_user.id, 
                    _('expense_select_category', value=abs(new_balance)), 
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            else:
                update_balance(new_balance)
                bot.send_message(message.from_user.id, _('balance_updated', value=new_balance), parse_mode='Markdown')
        except ValueError:
            bot.send_message(message.from_user.id, _('balance_invalid_format'))

def get_balance(month = -1):
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)

        if month == -1:
            month = datetime.datetime.now().strftime('%B')
        
        return round(data['year'].get(month, {}).get('balance', 0), 2), round(data['year'].get(month, {}).get('saldo', 0), 2)
    except Exception as e:
        logging.error(f"Error in get_balance: {e}")
        raise

def get_full_balance():
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logging.error(f"Error in get_full_balance: {e}")
        raise

def update_balance(new_balance: float, category: str = None):
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)

        month = datetime.datetime.now().strftime('%B')
        day = int(datetime.datetime.now().strftime('%d'))

        data['year'][month]['balance'] += new_balance
        data['year'][month]['saldo'] += new_balance
        
        if new_balance > 0:
            data['income'][day - 1] += new_balance
        else:
            expense = abs(new_balance)
            data['expenses'][day - 1] += expense
            
            if category:
                if 'categories' not in data:
                    data['categories'] = {
                        'important': 0,
                        'unplanned': 0,
                        'repetable': 0,
                        'optional': 0,
                        'uncategorized': 0
                    }

                if 'categories' not in data['year'][month]:
                    data['year'][month]['categories'] = {
                        'important': 0,
                        'unplanned': 0,
                        'repetable': 0,
                        'optional': 0,
                        'uncategorized': 0
                    }

                if category not in data['categories']:
                    data['categories'][category] = 0
                if category not in data['year'][month]['categories']:
                    data['year'][month]['categories'][category] = 0

                data['categories'][category] += expense
                data['year'][month]['categories'][category] += expense

        with open(balance_file_path, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logging.info(f"Balance updated: {new_balance}" + 
                     (f", category: {category}" if category and new_balance < 0 else ""))
    except Exception as e:
        logging.error(f"Error in update_balance: {e}")
        raise

def forecast_balance_and_saldo(data: dict):
    try:
        months = list(data['year'].keys())
        month = datetime.datetime.now().month
        balances = [data['year'][month].get('balance', 0) for month in months]
        saldos = [data['year'][month].get('saldo', 0) for month in months]

        balances = np.nan_to_num(balances)
        saldos = np.nan_to_num(saldos)

        X = np.arange(len(months)).reshape(-1, 1)
        y_saldo = np.array(saldos)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model_saldo = LinearRegression()
        model_saldo.fit(X_scaled, y_saldo)
        forecast_saldo_current = model_saldo.predict(scaler.transform([[len(months)]]))[0]
        forecast_saldo_next = model_saldo.predict(scaler.transform([[len(months) + 1]]))[0]

        forecast_balance_current = balances[month - 2] + forecast_saldo_current
        forecast_balance_next = balances[month - 1] + forecast_saldo_next

        return (forecast_balance_current, forecast_saldo_current), (forecast_balance_next, forecast_saldo_next)
    except Exception as e:
        logging.error(f"Error in forecast_balance_and_saldo: {e}")

def generate_report_data(data):
    try:
        plot_income_expenses(data)
        plot_categories(data)
        
        forecast_result = forecast_balance_and_saldo(data)
        if forecast_result:
            (forecast_balance_current, forecast_saldo_current), (forecast_balance_next, forecast_saldo_next) = forecast_result
        else:
            forecast_balance_current = forecast_saldo_current = forecast_balance_next = forecast_saldo_next = 0

        months = list(data['year'].keys())
        month = datetime.datetime.now().strftime('%B')
        balances = [data['year'][month].get('balance', 0) for month in months]
        saldos = [data['year'][month].get('saldo', 0) for month in months]
        avg_balance = sum(balances) / len(balances) if balances else 0
        avg_saldo = sum(saldos) / len(saldos) if saldos else 0
        max_balance = max(balances) if balances else 0
        min_balance = min(balances) if balances else 0
        max_balance_month = months[balances.index(max_balance)] if balances else ""
        min_balance_month = months[balances.index(min_balance)] if balances else ""
        total_income = sum(data['income'])
        total_expenses = sum(data['expenses'])

        caption = (
            f'{_("balance_report_title")}\n\n'
            f'{_("balance_forecast_current", value=round(forecast_balance_current, 2))}\n'
            f'{_("balance_forecast_saldo_current", value=round(forecast_saldo_current, 2))}\n'
            f'{_("balance_forecast_next", value=round(forecast_balance_next, 2))}\n'
            f'{_("balance_forecast_saldo_next", value=round(forecast_saldo_next, 2))}\n\n'
            f'{_("balance_current_income", value=total_income)}\n'
            f'{_("balance_current_expenses", value=total_expenses)}\n\n'
            f'{_("balance_avg_year", value=round(avg_balance, 2))}\n'
            f'{_("balance_avg_saldo_year", value=round(avg_saldo, 2))}\n'
            f'{_("balance_max_year", value=round(max_balance, 2), month=max_balance_month)}\n'
            f'{_("balance_min_year", value=round(min_balance, 2), month=min_balance_month)}\n\n'
            f'{_("balance_total_year", value=round(sum(saldos), 2))}'
        )
        
        return caption
    except Exception as e:
        logging.error(f"Error in generate_report_data: {e}")
        return None

def report(bot: telebot, USER_ID: str):
    try:
        data = get_full_balance()
        separate_graphs = plot_balance(data)
        caption = generate_report_data(data)
        
        media = []
        media.append(telebot.types.InputMediaPhoto(open('balance_plot.png', 'rb'), caption=caption, parse_mode='Markdown'))
        
        if separate_graphs:
            try:
                media.append(telebot.types.InputMediaPhoto(open('saldo_plot.png', 'rb')))
            except Exception as e:
                logging.error(f"Error adding saldo plot: {e}")
        
        try:
            media.append(telebot.types.InputMediaPhoto(open('income_expenses_plot.png', 'rb')))
        except Exception as e:
            logging.error(f"Error adding income expenses plot: {e}")
            
        try:
            media.append(telebot.types.InputMediaPhoto(open('categories_plot.png', 'rb')))
        except Exception as e:
            logging.error(f"Error adding categories plot: {e}")

        bot.send_media_group(USER_ID, media)

        os.remove('balance_plot.png')
        if separate_graphs:
            try:
                os.remove('saldo_plot.png')
            except:
                pass
            
        try:
            os.remove('income_expenses_plot.png')
        except:
            pass
            
        try:
            os.remove('categories_plot.png')
        except:
            pass
    except Exception as e:
        bot.send_message(USER_ID, _('balance_report_error'))
        logging.error(f'Error while sending report: {e}')

def balance_reset(bot, user_id):
    try:
        if not os.path.exists('data/balance.json'):
            logging.error("File balance.json doesn't exist")
            return
            
        with open('data/balance.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        months = list(data["year"].keys())
        now = datetime.datetime.now()
        current_month = now.strftime("%B")
        
        if current_month == "July" and "Jule" in data["year"]:
            current_month = "Jule"
        
        try:
            current_index = months.index(current_month)
        except ValueError:
            logging.error(f"The month {current_month} doesn't exist in the balance data")
            bot.send_message(user_id, _('balance_reset_month_not_found', month=current_month))
            return
            
        prev_index = (current_index - 1) % 12
        prev_month = months[prev_index]
        prev_balance = data["year"][prev_month]["balance"]
        
        caption = generate_report_data(data)
        separate_graphs = plot_balance(data)
        
        data["year"][current_month]["balance"] = prev_balance
        data["year"][current_month]["saldo"] = 0
        
        if 'categories' in data["year"][current_month]:
            data["year"][current_month]["categories"] = {
                'important': 0,
                'unplanned': 0,
                'optional': 0,
                'uncategorized': 0
            }
        
        data["income"] = [0] * 31
        data["expenses"] = [0] * 31
        
        with open('data/balance.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            
        reset_info = (
            f"*{_('balance_reset_title')}*\n\n"
            f"{_('balance_reset_message', value=prev_balance, month=prev_month)}\n"
            f"{_('balance_reset_saldo')}\n"
            f"{_('balance_reset_daily')}\n"
            f"{_('balance_reset_categories')}\n\n"
        )
        
        full_caption = reset_info + caption
        
        media = []
        media.append(telebot.types.InputMediaPhoto(open('balance_plot.png', 'rb'), caption=full_caption, parse_mode='Markdown'))
        
        if separate_graphs:
            try:
                media.append(telebot.types.InputMediaPhoto(open('saldo_plot.png', 'rb')))
            except Exception as e:
                logging.error(f"Error adding saldo plot: {e}")
        
        try:
            media.append(telebot.types.InputMediaPhoto(open('income_expenses_plot.png', 'rb')))
        except Exception as e:
            logging.error(f"Error adding income_expenses_plot: {e}")
            
        try:
            media.append(telebot.types.InputMediaPhoto(open('categories_plot.png', 'rb')))
        except Exception as e:
            logging.error(f"Error adding categories_plot: {e}")

        bot.send_media_group(user_id, media)
        
        try:
            os.remove('balance_plot.png')
            
            if separate_graphs:
                try:
                    os.remove('saldo_plot.png')
                except Exception as e:
                    logging.error(f"Error removing saldo plot: {e}")
            
            try:
                os.remove('income_expenses_plot.png')
            except Exception as e:
                logging.error(f"Error removing income_expenses_plot: {e}")
                
            try:
                os.remove('categories_plot.png')
            except Exception as e:
                logging.error(f"Error removing categories_plot: {e}")
                
        except Exception as e:
            logging.error(f"Error removing plot files: {e}")
            
        logging.info(f"Balance reset: {prev_month} -> {current_month}, balance: {prev_balance}")
        return True
        
    except Exception as e:
        logging.error(f"Error during balance reset: {e}")
        bot.send_message(user_id, _('balance_reset_error', error=str(e)))
        return False
    
def init_categories():
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)
        
        if 'categories' not in data:
            data['categories'] = {
                'important': 0,
                'unplanned': 0,
                'repetable': 0,
                'optional': 0,
                'uncategorized': 0
            }

            with open(balance_file_path, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            logging.info("Expense categories initialized")

        for month in data['year']:
            if 'categories' not in data['year'][month]:
                data['year'][month]['categories'] = {
                    'important': 0,
                    'unplanned': 0,
                    'repetable': 0,
                    'optional': 0,
                    'uncategorized': 0
                }

        with open(balance_file_path, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error initializing expense categories: {e}")

def handle_expense_category(call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    try:
        parts = call.data.split('_')
        category = parts[2]
        if category == 'repetable':
            category = 'repetable'
        amount = float(parts[3])
        
        if category != 'uncategorized':
            with open(balance_file_path, 'r') as file:
                data = json.load(file)

            month = datetime.datetime.now().strftime('%B')

            for cat in ['uncategorized', category]:
                if cat not in data['categories']:
                    data['categories'][cat] = 0
                if cat not in data['year'][month]['categories']:
                    data['year'][month]['categories'][cat] = 0

            data['categories']['uncategorized'] -= amount
            data['year'][month]['categories']['uncategorized'] -= amount

            data['categories'][category] += amount
            data['year'][month]['categories'][category] += amount

            with open(balance_file_path, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        
        category_name = _(f"expense_{category}")
        bot.edit_message_text(
            _('expense_category_selected', value=amount, category=category_name),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        bot.answer_callback_query(call.id, _('expense_category_saved'))
    except Exception as e:
        logging.error(f"Error handling expense category: {e}")
        bot.answer_callback_query(call.id, _('error_occurred'))