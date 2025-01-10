import datetime
import schedule
import telebot
import logging
import time
import os
from dotenv import load_dotenv
from libs.notification import *
from libs.balance import *
from libs.support import *
from libs.email import *
from libs.files import *
from libs.task import *
from libs.vps import *

# TODO: restruct yaer data, add dataclasses
# TODO: add configs
# TODO: validate configs on start
# TODO: creating directories on start
# TODO: add install script
# TODO: add multilanguage support

#########################
#                       #
#        CONFIGS        #
#                       #
#########################

load_dotenv()

logging.basicConfig(
    filename='./secretary.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

bot = telebot.TeleBot(BOT_TOKEN)

logging.debug('Starting secretary bot')

#########################
#                       #
#       FUNCTIONS       #
#                       #
#########################

def check(id):
    if (id == int(USER_ID)):
        return True
    else:
        bot.send_message(id, 'У вас нет прав для выполнения этой команды')
        return False

def everyday_job():
    try:
        day = datetime.datetime.now().strftime('%d')
        logging.info(f'Everyday job started. Day: {day}')
        if day == '01':
            balance_reset(bot, USER_ID)

            tasks = read_json()
            tasks["complete"] = 0
            
            with open('data/tasks.json', 'w') as file:
                json.dump(tasks, file, indent=4, ensure_ascii=False)
            
            logging.info('Statistic reset')
    
        clean_logs()
        logging.info("Логи очищены")

        tasks = read_json()
        count = len(tasks["tasks"])
        completed = tasks["complete"]
        balance, saldo = get_balance()
        bot.send_message(USER_ID, f'*Краткая сводка на день*\n\nБаланс: `{balance}`\nСальдо: `{saldo}`\n\nЗадачи: `{count}`\nВыполнено в этом месяце: `{completed}`', parse_mode='Markdown')

    except Exception as e:
        logging.error(f'Error in everyday_job: {e}')

def main():
    if not os.path.exists('files'):
        os.makedirs('files')
    if not os.path.exists('public_files'):
        os.makedirs('public_files')
    everyday_job()
    schedule.every().day.at("00:00").do(everyday_job)
    bot.send_message(USER_ID, 'Секретарь запущен')
    logging.info('Secretary bot started')
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            time.sleep(15)

#########################
#                       #
#        COMMANDS       #
#                       #
#########################

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.from_user.id, ('Приветствую! Я бот - личный секретарь.\n'
                    'Своего босса не раскрою, но если хотите себе такого же, введите /link.\n'
                    'Если хотите узнать, что я умею, введите /help.\n'
                    'Чтобы написать моему боссу анонимное сообщение, введите /call.'))

@bot.message_handler(commands=['link'])
def link(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.from_user.id, 'https://github.com/ivanvit100')

@bot.message_handler(commands=['balance'])
def balance(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    balance_main(message, bot)

@bot.message_handler(commands=['report'])
def rpt(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    report(bot, USER_ID)

@bot.message_handler(commands=['call'])
def call(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    message_parts = message.text.split(' ')
    if message.from_user.id != int(USER_ID) and len(message_parts) > 1:
        bot.send_message(int(USER_ID), f'Анонимное сообщение: \n\n{message.text[6:]}')
        bot.send_message(message.from_user.id, 'Сообщение отправлено')

@bot.message_handler(commands=['log'])
def log(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    get_log(message, bot)

@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')

    bot.send_message(message.from_user.id, (
        '*Список команд*\n\n'
        'Общедоступные команды:\n'
        '- /help - список команд\n'
        '- /call - написать владельцу бота\n'
        '- /pfiles - посмотреть список общедоступных файлов\n'
        '- /pdownload <название> - скачать общедоступный файл\n'
        '- /link - ссылка на исходный код бота\n\n'
        'Приватные команды:\n'
        '- /report - отчёт по балансу\n'
        '- /balance - текущий баланс\n'
        '- /balance <число> - изменить баланс на число\n'
        '- /notification <дата> <время> <сообщение> - уведомление\n'
        '- /notification - список уведомлений\n'
        '- /notification delete <номер> - удалить уведомление\n'
        '- /task <сообщение> - добавить задачу\n'
        '- /task - список задач\n'
        '- /task delete <номер> - удалить задачу\n'
        '- /email <address> <сообщение> - отправить сообщение на почту\n'
        '- /email - список сообщений на почту\n'
        '- /save - сохранить файл на веб-сервере\n'
        '- /share <название> - поделиться файлом\n'
        '- /download <название> - скачать файл\n'
        '- /delete <название> - удалить файл\n'
        '- /pdelete <название> - удалить общедоступный файл\n'
        '- /log - лог действий\n'
        '- /ssh <команда> - выполнить команду на сервере\n'
        '- /stats - статистика Beget'
    ), parse_mode='Markdown')

@bot.message_handler(commands=['ssh'])
def ssh_callback(message: telebot.types.Message):
    if not check(message.from_user.id):
        return
    ssh(message, bot)

@bot.message_handler(commands=['email'])
def email_command(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    email_main(message, bot)

@bot.message_handler(func=lambda message: message.text.startswith('/email_read_'))
def email_read_command(message: telebot.types.Message):
    if not check(message.from_user.id):
        return
    bot.send_chat_action(message.chat.id, 'typing')
    
    email_read(message, bot)

@bot.message_handler(content_types=['document'])
def save_file(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    try:
        if 'email' in message.caption.lower():
            email_main(message, bot, 1)
        else:
            save_doc(message, bot)
    except:
        save_doc(message, bot)

@bot.message_handler(commands=["download"])
def download(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    download_file(message, bot, 1)

@bot.message_handler(commands=["files"])
def list_file(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    show_files(message, bot, 1)

@bot.message_handler(commands=["pdownload"])
def download(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    download_file(message, bot)

@bot.message_handler(commands=["pfiles"])
def list_file(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    show_files(message, bot)

@bot.message_handler(commands=["share"])
def share(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    share_file(message, bot)

@bot.message_handler(commands=["delete"])
def delete(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    delete_file(message, bot, 1)

@bot.message_handler(commands=["pdelete"])
def delete(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    delete_file(message, bot)

@bot.message_handler(commands=["stats"])
def stats(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    get_vps_data(message, bot)

@bot.message_handler(commands=['notification'])
def handle_schedule(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.chat.id):
        return
    
    message_parts = message.text.split(' ')
    
    try:
        if len(message_parts) < 3:
            schedule_list(bot)
    
        elif message_parts[1] == 'delete':
            job_id = int(message_parts[2])
            cancel_scheduled_message(job_id)
            bot.reply_to(message, f'Уведомление {job_id} удалено.')
    
        else:
            _, date, run_at, msg = message.text.split(' ', 3)
            run_at = f"{date} {run_at}"
            schedule_message(msg, run_at, bot)
            logging.info(f'Notification scheduled: {run_at} {msg}')
            bot.reply_to(message, f'Сообщение будет отправлено в {run_at}.')
    
    except Exception as e:
        logging.error(f'Error in handle_schedule: {e}')
        bot.reply_to(message, 'Произошла ошибка.')

@bot.message_handler(commands=['task'])
def handle_task(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.chat.id):
        return
    
    message_parts = message.text.split(' ')
    
    try:
        if len(message_parts) < 2:
            tasks_list(message, bot)
        elif message_parts[1] == 'delete':
            task_done(message, bot)
        else:
            task_add(message, bot)
    
    except Exception as e:
        logging.error(f'Error in handle_task: {e}')
        bot.reply_to(message, 'Произошла ошибка.')

@bot.message_handler(func=lambda message: message.text.startswith('/task_done_'))
def handle_task_done(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.chat.id):
        return
    
    task_done(message, bot)



if __name__ == '__main__':
    main()