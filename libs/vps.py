import requests
import logging
import telebot
import os
from dotenv import load_dotenv

load_dotenv()

VPS_USER_STATS = os.getenv('VPS_USER_STATS')

def get_vps_data(message: telebot.types.Message, bot: telebot.TeleBot):
    url = VPS_USER_STATS
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()['answer']['result']
        bot.send_message(message.from_user.id, (
            f'*Информация о VPS*\n\n'
            f'Процессор `{data["server_cpu_name"]}`\n'
            f'ОЗУ `{data["server_memorycurrent"]}/{data["server_memory"]}`\n'
            f'Диск `{data["user_quota"]}/{data["plan_quota"]}`\n\n'
            f'*Общая статистика*\n\n'
            f'Сайтов `{data["user_sites"]}`\n'
            f'Доменов `{data["user_domains"]}`\n'
            f'FTP `{data["user_ftp"]}`\n'
            f'Баз данных `{data["user_mysqlsize"]}`\n'
            f'Почтовых ящиков `{data["user_mail"]}`\n\n'
            f'*Тариф* `{data["plan_name"]}`\n\n'
            f'Стоимость\n'
            f'`{data["user_rate_current"]}` руб в день\n'
            f'`{data["user_rate_month"]}` руб в месяц\n'
            f'`{data["user_rate_year"]}` руб в год\n'
            f'Баланс `{data["user_balance"]}` руб\n'
            f'Оплачено на `{data["user_days_to_block"]}` дней\n\n'
            f'Загрузка `{round(data['server_loadaverage'], 2)}`\n'
            f'Время работы `{data['server_uptime']}` часов\n'
        ), parse_mode='Markdown')
    else:
        bot.send_message(message.from_user.id, 'Произошла ошибка')
        logging.error(f"Ошибка: {response.status_code}")