import subprocess
import datetime
import schedule
import telebot
import logging
import shlex
import time
import os
from dotenv import load_dotenv
from weasyprint import HTML # type: ignore
from telebot import types
from libs.balance import *
from libs.email import *

# +TODO: /start - приветствие
# +TODO: /help - список команд
# +TODO: /call - написать владельцу бота
# +TODO: /report - отчёт по балансу
# +TODO: /balance - текущий баланс
# +TODO: /balance <число> - изменить баланс на число
# TODO: /notification <дата> <время> <сообщение> - уведомление
# TODO: /notification list - список уведомлений
# TODO: /notification delete <номер> - удалить уведомление
# TODO: /task <сообщение> - добавить задачу
# TODO: /task list - список задач
# TODO: /task delete <номер> - удалить задачу
# +TODO: /email <address> <сообщение> - отправить сообщение на почту
# +TODO: /email - список сообщений на почту
# TODO: /save - сохранить файл на веб-сервере
# TODO: /share <название> - поделиться файлом
# TODO: /delete <название> - удалить файл
# +TODO: /log - лог действий
# +TODO: /ssh <команда> - выполнить команду на сервере
# TODO: /stats - статистика Beget

# TODO: restruct yaer data, add dataclasses

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
            data = get_full_balance()
            current_month = datetime.datetime.now().strftime('%B')
            previous_month = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%B')
            previous_balance = data['year'].get(previous_month, {}).get('balance', 0)
            
            report(bot, USER_ID)
            
            data['year'][current_month] = {
                'balance': previous_balance,
                'saldo': 0
            }
            data['income'] = [0] * 31
            data['expenses'] = [0] * 31
            
            with open(balance_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            logging.info('Monthly report was sent and balances were reset')
    except Exception as e:
        logging.error(f'Error in everyday_job: {e}')

def main():
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
    bot.send_message(message.from_user.id, 'Приветствую! Я бот - личный секретарь. Своего босса не раскрою, но если хотите себе такого же, введите /link.\nЕсли хотите узнать, что я умею, введите /help.\nЧтобы написать моему боссу анонимное сообщение, введите /call.')

@bot.message_handler(commands=['link'])
def link(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.from_user.id, 'https://github.com/ivanvit100')

@bot.message_handler(commands=['balance'])
def balance(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    message_parts = message.text.split(' ')
    if len(message_parts) == 1:
        data = get_full_balance()
        mounth_plot(data)
        current_balance, current_saldo = get_balance()
        month = datetime.datetime.now().strftime('%B')
        caption = f'Текущий месяц: {month}\n\nВаш баланс: `{current_balance}`\nСальдо: `{current_saldo}`'
        with open('mounth_plot.png', 'rb') as photo:
            bot.send_photo(message.from_user.id, photo, caption=caption, parse_mode='Markdown')
        os.remove('mounth_plot.png')
    else:
        try:
            new_balance = float(message_parts[1])
            update_balance(new_balance)
            bot.send_message(message.from_user.id, f'Баланс обновлен: `{new_balance}`', parse_mode='Markdown')
        except ValueError:
            bot.send_message(message.from_user.id, 'Неверный формат параметра')

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
    
    with open('./secretary.log', 'r') as file:
        lines = file.readlines()
        log = ''.join(lines[-25:])
    bot.send_message(message.from_user.id, log)

@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')

    bot.send_message(message.from_user.id, (
        'Список команд:\n\n'
        '/start - приветствие\n'
        '/help - список команд\n'
        '/call - написать владельцу бота\n'
        '/report - отчёт по балансу\n'
        '/balance - текущий баланс\n'
        '/balance <число> - изменить баланс на число\n'
        '/notification <дата> <время> <сообщение> - уведомление\n'
        '/notification list - список уведомлений\n'
        '/notification delete <номер> - удалить уведомление\n'
        '/task <сообщение> - добавить задачу\n'
        '/task list - список задач\n'
        '/task delete <номер> - удалить задачу\n'
        '/email <address> <сообщение> - отправить сообщение на почту\n'
        '/email - список сообщений на почту\n'
        '/save - сохранить файл на веб-сервере\n'
        '/share <название> - поделиться файлом\n'
        '/delete <название> - удалить файл\n'
        '/log - лог действий\n'
        '/ssh <команда> - выполнить команду на сервере\n'
        '/stats - статистика Beget'
    ))

@bot.message_handler(commands=['ssh'])
def ssh(message: telebot.types.Message):
    if not check(message.from_user.id):
        return
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        message_parts = shlex.split(message.text)
        command = message_parts[1]
        params = [part for part in message_parts[2:] if not part.startswith('-')]
        flags = [part for part in message_parts[2:] if part.startswith('-')]

        if 'sudo' in message_parts:
            logging.warning(f'User {message.from_user.id} tried to use sudo')
            bot.send_message(message.from_user.id, "Использование команды 'sudo' запрещено.")
            return

        result = subprocess.run([command] + params + flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            bot.send_message(message.from_user.id, f'Результат выполнения команды:\n\n```{result.stdout}```', parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, f'Ошибка выполнения команды:\n\n```{result.stderr}```', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.from_user.id, "Произошла ошибка")
        logging.error(f'Error in ssh: {e}')

@bot.message_handler(commands=['email'])
def email_command(message: telebot.types.Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not check(message.from_user.id):
        return
    
    message_parts = message.text.split(' ')
    if len(message_parts) < 2:
        emails = emails_list()
        if not emails:
            bot.send_message(message.from_user.id, 'Нет новых сообщений')
            return

        email_list = ""
        for index, email in enumerate(emails):
            email_list += f"{index + 1}. {email['From']}:\n{email['Subject']}\nПрочесть: /email\_read\_{index}\n\n"

        bot.send_message(message.from_user.id, f'Список последних сообщений для `{EMAIL_ADDRESS}`:\n\n{email_list}', parse_mode='Markdown')
        return
    
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        template = os.path.join(current_directory, 'data', 'email.html')

        send_email(message_parts[1], ' '.join(message_parts[2:]), template)
        
        bot.send_message(message.from_user.id, 'Сообщение отправлено на почту')
    except Exception as e:
        logging.error(f'Error in email: {e}')
        bot.send_message(message.from_user.id, 'Произошла ошибка')

@bot.message_handler(func=lambda message: message.text.startswith('/email_read_'))
def email_read_command(message: telebot.types.Message):
    if not check(message.from_user.id):
        return
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        email_index = int(message.text.split('_')[-1])
        
        email = email_read(email_index)
        email_html = f"<h1>{email['From']}</h1><h2>{email['Subject']}</h2><p>{email['Body']}</p>"
        
        pdf_path = f"/tmp/email_{email_index}.pdf"
        HTML(string=email_html).write_pdf(pdf_path)
        
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(message.from_user.id, pdf_file)
        
        os.remove(pdf_path)
    except Exception as e:
        logging.error(f"Error handling email_read command: {e}")
        bot.send_message(message.from_user.id, 'Произошла ошибка при обработке сообщения')



if __name__ == '__main__':
    main()