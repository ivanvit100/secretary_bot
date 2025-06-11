import requests
import logging
import telebot
import os
from dotenv import load_dotenv
from i18n import _

load_dotenv()

VPS_USER_STATS = os.getenv('VPS_USER_STATS')

def get_vps_data(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        url = VPS_USER_STATS
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()['answer']['result']
            bot.send_message(message.from_user.id, (
                f'*{_("vps_info_title")}*\n\n'
                f'{_("vps_cpu")} `{data["server_cpu_name"]}`\n'
                f'{_("vps_ram")} `{data["server_memorycurrent"]}/{data["server_memory"]}`\n'
                f'{_("vps_disk")} `{data["user_quota"]}/{data["plan_quota"]}`\n\n'
                f'*{_("vps_general_stats")}*\n\n'
                f'{_("vps_sites")} `{data["user_sites"]}`\n'
                f'{_("vps_domains")} `{data["user_domains"]}`\n'
                f'{_("vps_ftp")} `{data["user_ftp"]}`\n'
                f'{_("vps_databases")} `{data["user_mysqlsize"]}`\n'
                f'{_("vps_mailboxes")} `{data["user_mail"]}`\n\n'
                f'*{_("vps_tariff")}* `{data["plan_name"]}`\n\n'
                f'{_("vps_cost")}\n'
                f'`{data["user_rate_current"]}` {_("vps_rub_per_day")}\n'
                f'`{data["user_rate_month"]}` {_("vps_rub_per_month")}\n'
                f'`{data["user_rate_year"]}` {_("vps_rub_per_year")}\n'
                f'{_("vps_balance")} `{data["user_balance"]}` {_("vps_rub")}\n'
                f'{_("vps_paid_for")} `{data["user_days_to_block"]}` {_("vps_days")}\n\n'
                f'{_("vps_load")} `{round(data["server_loadaverage"], 2)}`\n'
                f'{_("vps_uptime")} `{data["server_uptime"]}` {_("vps_hours")}\n'
            ), parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, _('vps_error'))
            logging.error(f"Error: {response.status_code}")
    except Exception as e:
        bot.send_message(message.from_user.id, _('vps_error'))
        logging.error(f"Error in get_vps_data: {e}")