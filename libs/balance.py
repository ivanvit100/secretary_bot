import os
import json
import telebot
import logging
import datetime
import numpy as np # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore
from sklearn.linear_model import LinearRegression # type: ignore
from libs.plots import *

current_dir = os.path.dirname(os.path.abspath(__file__))
balance_file_path = os.path.join(current_dir, '../data/balance.json')

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
            f'Отчёт по балансу\n\n'
            f'Прогнозированный баланс на текущий месяц: `{round(forecast_balance_current, 2)}`\n'
            f'Прогнозированное сальдо на текущий месяц: `{round(forecast_saldo_current, 2)}`\n'
            f'Прогнозированный баланс на следующий месяц: `{round(forecast_balance_next, 2)}`\n'
            f'Прогнозированное сальдо на следующий месяц: `{round(forecast_saldo_next, 2)}`\n\n'
            f'Текущие доходы: `{total_income}`\n'
            f'Текущие расходы: `{total_expenses}`\n\n'
            f'Средний баланс за год: `{round(avg_balance, 2)}`\n'
            f'Среднее сальдо за год: `{round(avg_saldo, 2)}`\n'
            f'Максимальный баланс за год: `{round(max_balance, 2)}` ({max_balance_month})\n'
            f'Минимальный баланс за год: `{round(min_balance, 2)}` ({min_balance_month})\n\n'
            f'Итоговый приход за год: `{round(sum(saldos), 2)}`\n'
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
        bot.send_message(USER_ID, f'Произошла ошибка при отправке отчёта.')
        logging.error(f'Error while sending report: {e}')