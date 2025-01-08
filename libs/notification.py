import datetime
import telebot
import logging
import os
from dotenv import load_dotenv
from threading import Timer

load_dotenv()

scheduled_jobs = []
USER_ID = os.getenv('USER_ID')

def send_delayed_message(message: str, bot: telebot.TeleBot):
    bot.send_message(USER_ID, f'*Внимание!* Новое уведомление!\n\n{message}', parse_mode="Markdown")

def schedule_message(message: str, run_at: str, bot: telebot.TeleBot):
    run_at_datetime = datetime.datetime.strptime(run_at, '%d.%m.%Y %H:%M')
    delay = (run_at_datetime - datetime.datetime.now() - datetime.timedelta(hours=3)).total_seconds()
    
    if delay > 0:
        timer = Timer(delay, send_delayed_message, [message, bot])
        scheduled_jobs.append((run_at, message, timer))
        timer.start()
        logging.info(f"Scheduled message at {run_at}")
    else:
        logging.warning(f"Cannot schedule message in the past: {run_at}")

def cancel_scheduled_message(index: int):
    if 0 <= index < len(scheduled_jobs):
        scheduled_jobs[index][2].cancel()
        del scheduled_jobs[index]
        logging.info(f"Cancelled scheduled message with index {index}")
    else:
        logging.warning(f"No scheduled job found with index {index}")

def schedule_list(bot: telebot.TeleBot):
    if scheduled_jobs:
        messages = [f"`{i}`: __{job[0]}__ - {job[1]}" for i, job in enumerate(scheduled_jobs)]
        bot.send_message(USER_ID, "*Уведомления*:\n\n" + "\n".join(messages), parse_mode="Markdown")
    else:
        bot.send_message(USER_ID, "У вас нет запланированных уведомлений.")