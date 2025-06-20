import os
import json
import telebot
import logging
import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
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

def update_balance(new_balance: float):
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)

        month = datetime.datetime.now().strftime('%B')
        day = int(datetime.datetime.now().strftime('%d'))

        data['year'][month]['balance'] += new_balance
        data['year'][month]['saldo'] += new_balance
        data['income'][day - 1] += new_balance if new_balance > 0 else 0
        data['expenses'][day - 1] += -new_balance if new_balance < 0 else 0

        with open(balance_file_path, 'w') as file:
            json.dump(data, file, indent=4)

        logging.info("Balance updated")
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

def report(bot: telebot, USER_ID: str):
    try:
        data = get_full_balance()
        plot_balance(data)
        plot_income_expenses(data)
        (forecast_balance_current, forecast_saldo_current), (forecast_balance_next, forecast_saldo_next) = forecast_balance_and_saldo(data)

        months = list(data['year'].keys())
        balances = [data['year'][month].get('balance', 0) for month in months]
        saldos = [data['year'][month].get('saldo', 0) for month in months]
        avg_balance = sum(balances) / len(balances)
        avg_saldo = sum(saldos) / len(saldos)
        max_balance = max(balances)
        min_balance = min(balances)
        max_balance_month = months[balances.index(max_balance)]
        min_balance_month = months[balances.index(min_balance)]
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
            f'{_("balance_total_year", value=round(sum(saldos), 2))}\n'
        )

        media = []
        media.append(telebot.types.InputMediaPhoto(open('balance_plot.png', 'rb'), caption=caption, parse_mode='Markdown'))
        try:
            media.append(telebot.types.InputMediaPhoto(open('income_expenses_plot.png', 'rb')))
        except:
            pass

        bot.send_media_group(USER_ID, media)

        os.remove('balance_plot.png')
        try:
            os.remove('income_expenses_plot.png')
        except:
            pass
    except Exception as e:
        bot.send_message(USER_ID, _('balance_report_error'))
        logging.error(f'Error while sending report: {e}')

def balance_reset(bot, user_id):
    try:
        if not os.path.exists('data/balance.json'):
            logging.error("Файл balance.json не существует")
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
            logging.error(f"Не найден месяц {current_month} в файле баланса")
            bot.send_message(user_id, _('balance_reset_month_not_found', month=current_month))
            return
            
        prev_index = (current_index - 1) % 12
        prev_month = months[prev_index]
        
        prev_balance = data["year"][prev_month]["balance"]
        
        data["year"][current_month]["balance"] = prev_balance
        data["year"][current_month]["saldo"] = 0
        
        data["income"] = [0] * 31
        data["expenses"] = [0] * 31
        
        with open('data/balance.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            
        msg = f"*{_('balance_reset_title')}*\n\n"
        msg += f"{_('balance_reset_message', value=prev_balance, month=prev_month)}\n"
        msg += f"{_('balance_reset_saldo')}\n"
        msg += f"{_('balance_reset_daily')}"
        
        bot.send_message(user_id, msg, parse_mode="Markdown")
        logging.info(f"Баланс сброшен: {prev_month} -> {current_month}, balance: {prev_balance}")
        
        return True
        
    except Exception as e:
        logging.error(f"Ошибка при сбросе баланса: {e}")
        bot.send_message(user_id, _('balance_reset_error', error=str(e)))
        return False