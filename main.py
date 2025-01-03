import datetime
import schedule
import telebot
import logging
import time
import os
from dotenv import load_dotenv
from libs.balance import *
from libs.support import *
from libs.email import *
from libs.files import *

# +TODO: /start - приветствие
# +TODO: /help - список команд
# +TODO: /call - написать владельцу бота
# +TODO: /report - отчёт по балансу
# +TODO: /balance - текущий баланс
# +TODO: /balance <число> - изменить баланс на число
# TODO: /notification <дата> <время> <сообщение> - уведомление
# TODO: /notification - список уведомлений
# TODO: /notification delete <номер> - удалить уведомление
# TODO: /task <сообщение> - добавить задачу
# TODO: /task - список задач
# TODO: /task delete <номер> - удалить задачу
# +TODO: /email <address> <сообщение> - отправить сообщение на почту
# +TODO: /email - список сообщений на почту
# +TODO: Сохранить файл на веб-сервере
# +TODO: /files - Список файлов
# +TODO: /share <название> - поделиться файлом
# +TODO: /delete <название> - удалить файл
# +TODO: /download <название> - скачать файл
# +TODO: /log - лог действий
# +TODO: /ssh <команда> - выполнить команду на сервере
# TODO: /stats - статистика Beget

# TODO: restruct yaer data, add dataclasses
# TODO: auto log clearing

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
    # TODO: todo and notifications
    try:
        day = datetime.datetime.now().strftime('%d')
        logging.info(f'Everyday job started. Day: {day}')
        if day == '01':
            balance_reset(bot, USER_ID)
            
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
    
    email_main(message)

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



if __name__ == '__main__':
    main()