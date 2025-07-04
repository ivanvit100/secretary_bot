import threading
import datetime
import schedule
import logging
import config
import time
import os
import json
import libs.menu
from modules.callbacks import register_callbacks
from modules.handlers import register_handlers
from modules.keyboard import register_keyboard
from libs.balance import balance_reset, get_balance
from libs.task import read_json
from libs.support import clean_logs
from i18n import _

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

#########################
#                       #
#       FUNCTIONS       #
#                       #
#########################

def check(id, bot):
    if (id == int(USER_ID)):
        return True
    else:
        bot.send_message(id, _('no_permission'))
        return False

def everyday_job(bot):
    try:
        day = datetime.datetime.now().strftime('%d')
        logging.info(f'Everyday job started. Day: {day}')
        if day == '01':
            if config.MODULES["balance"]:
                balance_reset(bot, USER_ID)

            if config.MODULES["task"]:
                tasks = read_json()
                tasks["complete"] = 0
                
                with open('data/tasks.json', 'w') as file:
                    json.dump(tasks, file, indent=4, ensure_ascii=False)
            
            logging.info('Statistic reset')
    
        clean_logs()
        logging.info("Logs cleared")

        message = f'*{_("daily_summary_title")}*\n\n'
        
        if config.MODULES["balance"]:
            balance, saldo = get_balance()
            message += f'{_("daily_balance")}: `{balance}`\n{_("daily_saldo")}: `{saldo}`\n\n'
            
        if config.MODULES["task"]:
            tasks = read_json()
            count = len(tasks["tasks"])
            completed = tasks["complete"]
            message += f'{_("daily_tasks")}: `{count}`\n{_("daily_completed")}: `{completed}`'
        
        markup = None
        if config.MODULES["notification"]:
            from libs.notification import get_today_notifications_markup
            today_notifications_markup = get_today_notifications_markup()
            
            if today_notifications_markup:
                message += f'\n\n*{_("daily_notifications_title")}*'
                markup = today_notifications_markup
        
        bot.send_message(
            USER_ID, 
            message, 
            parse_mode='Markdown',
            reply_markup=markup
        )

    except Exception as e:
        logging.error(f'Error in everyday_job: {e}')

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    from main import bot
    
    if not os.path.exists('files'):
        os.makedirs('files')
    if not os.path.exists('public_files'):
        os.makedirs('public_files')
    if not os.path.exists('data'):
        os.makedirs('data')

    def local_check(user_id):
        return check(user_id, bot)
    
    if config.MODULES["balance"]:
        from libs.balance import init_categories
        init_categories()
    
    register_callbacks(bot, local_check)
    register_handlers(bot, local_check)
    register_keyboard(bot, local_check)
    
    report_time = (0 + config.UTC) % 24
    
    def scheduled_everyday_job():
        everyday_job(bot)
        
    schedule.every().day.at(f"{report_time:02d}:00").do(scheduled_everyday_job)
    
    scheduler_thread = threading.Thread(target=schedule_checker)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    if config.MODULES["notification"]:
        from libs.notification import init_notifications
        init_notifications(bot)
    
    libs.menu.show_reply_keyboard(USER_ID, bot)
    logging.info('Secretary bot started')
    
    everyday_job(bot)
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(15)