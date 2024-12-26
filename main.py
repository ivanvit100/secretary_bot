import datetime
import schedule
import telebot
import logging
import time
import os
from dotenv import load_dotenv
from libs.balance import *

# +TODO: /start - приветствие
# TODO: /help - список команд
# +TODO: /call - написать владельцу бота
# TODO: /report - отчёт по балансу
# +TODO: /balance - текущий баланс
# +TODO: /balance <число> - изменить баланс на число
# TODO: /notification <дата> <время> <сообщение> - уведомление
# TODO: /notification list - список уведомлений
# TODO: /notification delete <номер> - удалить уведомление
# TODO: /task <сообщение> - добавить задачу
# TODO: /task list - список задач
# TODO: /task delete <номер> - удалить задачу
# TODO: /email <сообщение> - отправить сообщение на почту
# TODO: /email list - список сообщений на почту
# TODO: /save - сохранить файл на веб-сервере
# TODO: /share - поделиться файлом
# +TODO: /log - лог действий
# TODO: /ssh <команда> - выполнить команду на сервере
# TODO: /stats - статистика Beget

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

def report():
    # TODO: fix forecast and second plot, add more info
    data = get_full_balance()
    plot_balance(data)
    plot_income_expenses(data)
    forecast_balance, forecast_saldo = forecast_balance_and_saldo(data)
    caption = f'Отчёт по балансу за прошлый месяц\n\nПрогнозированный баланс: {round(forecast_balance, 2)}\nПрогнозированное сальдо: {round(forecast_saldo, 2)}'
    
    media = []
    media.append(telebot.types.InputMediaPhoto(open('balance_plot.png', 'rb'), caption=caption))
    media.append(telebot.types.InputMediaPhoto(open('income_expenses_plot.png', 'rb'), caption='Доходы и расходы за прошлый месяц'))
    
    bot.send_media_group(USER_ID, media)
    
    os.remove('balance_plot.png')
    os.remove('income_expenses_plot.png')
    
    current_balance, _ = get_balance()
    update_balance(-current_balance)
    update_current_month_balance()

def everyday_job():
    day = datetime.datetime.now().strftime('%d')
    if (day == '01'):
        report()
        logging.info('Monthly report was sent')
    # TODO: todo and notifications

def main():
    everyday_job()
    schedule.every().day.at("00:00").do(everyday_job)
    bot.send_message(USER_ID, 'Секретарь запущен')
    logging.info('Secretary bot started')
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)

#########################
#                       #
#        COMMANDS       #
#                       #
#########################

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Приветствую! Я бот - личный секретарь. Своего босса не раскрою, но если хотите себе такого же, введите /link.\nЕсли хотите узнать, что я умею, введите /help.\nЧтобы написать моему боссу анонимное сообщение, введите /call.')

@bot.message_handler(commands=['link'])
def link(message):
    bot.send_message(message.from_user.id, 'https://github.com/ivanvit100')

@bot.message_handler(commands=['balance'])
def balance(message):
    if not check(message.from_user.id):
        return
    message_parts = message.text.split(' ')
    if len(message_parts) == 1:
        data = get_full_balance()
        plot_balance(data)
        current_balance, current_saldo = get_balance()
        month = datetime.datetime.now().strftime('%B')
        caption = f'Текущий месяц: {month}\n\nВаш баланс: {current_balance}\nСальдо: {current_saldo}'
        with open('balance_plot.png', 'rb') as photo:
            bot.send_photo(message.from_user.id, photo, caption=caption)
        os.remove('balance_plot.png')
    else:
        try:
            new_balance = float(message_parts[1])
            update_balance(new_balance)
            bot.send_message(message.from_user.id, f'Баланс обновлен: {new_balance}')
        except ValueError:
            bot.send_message(message.from_user.id, 'Неверный формат параметра')

@bot.message_handler(commands=['report'])
def rpt(message):
    if not check(message.from_user.id):
        return
    report()

@bot.message_handler(commands=['call'])
def call(message):
    message_parts = message.text.split(' ')
    if message.from_user.id != int(USER_ID) and len(message_parts) > 1:
        bot.send_message(int(USER_ID), f'Анонимное сообщение: \n\n{message.text[6:]}')
        bot.send_message(message.from_user.id, 'Сообщение отправлено')

@bot.message_handler(commands=['log'])
def log(message):
    if not check(message.from_user.id):
        return
    with open('./secretary.log', 'r') as file:
        lines = file.readlines()
        log = ''.join(lines[-25:])
    bot.send_message(message.from_user.id, log)



if __name__ == '__main__':
    main()