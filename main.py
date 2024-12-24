import os
import datetime
import schedule
import telebot
from dotenv import load_dotenv


# +TODO: /start - приветствие
# TODO: /help - список команд
# TODO: /call - написать владельцу бота
# TODO: /report - отчёт по балансу за прошлый месяц
# TODO: /report now - отчёт по балансу за текущий месяц
# TODO: /balance - текущий баланс
# TODO: /balance <число> - изменить баланс на число
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
# TODO: /log - лог действий
# TODO: /ssh <команда> - выполнить команду на сервере
# TODO: /stats - статистика Beget


#########################
#                       #
#       VARIABLES       #
#                       #
#########################

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

bot = telebot.TeleBot(BOT_TOKEN)

#########################
#                       #
#       FUNCTIONS       #
#                       #
#########################

def report():
    """
    Sends a report for the previous month if today is the first day of the month.
    """
    if datetime.datetime.now().day == 1:
        bot.send_message(USER_ID, 'Report for the last month')

def send_notification(message, date_time_str):
    """
    Sets a notification for a specific date and time.

    Parameters:
    message (str): The message to be sent.
    date_time_str (str): The date and time in the format 'dd.mm.yyyy HH:MM'.

    Returns:
    bool: True if the notification is successfully set, otherwise False.
    """
    try:
        date_time = datetime.datetime.strptime(date_time_str, '%d.%m.%Y %H:%M')
        delay = (date_time - datetime.datetime.now()).total_seconds()

        def task():
            bot.send_message(USER_ID, message)
            return schedule.CancelJob

        schedule.every(delay).seconds.do(task)
        return True
    except Exception:
        return False

def check(id):
    """
    Checks if the user has the rights to execute the command.

    Parameters:
    id (int): The user ID.

    Returns:
    bool: True if the user has the rights, otherwise False.
    """
    if (id == int(USER_ID)):
        return True
    else:
        bot.send_message(id, 'У вас нет прав для выполнения этой команды')
        return False

def main():
    """
    Starts the bot and sends a startup message.
    """
    bot.send_message(USER_ID, 'Секретарь запущен')
    bot.polling(none_stop=True)

#########################
#                       #
#       SCHEDULE        #
#                       #
#########################

schedule.every().day.at('00:00').do(report)

#########################
#                       #
#        COMMANDS       #
#                       #
#########################

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Приветствую! Я бот - личный секретарь. Своего босса не раскрою, но если хотите себе такого же, введите /link.\nЕсли хотите узнать, что я умею, введите /help.\nЧтобы написать моему боссу, введите /call.')

@bot.message_handler(commands=['link'])
def link(message):
    bot.send_message(message.from_user.id, 'https://github.com/ivanvit100')

@bot.message_handler(commands=['notification'])
def notification(message):
    if not check(message.from_user.id):
        return
    message_parts = message.text.split(' ')
    if len(message_parts) == 1:
        bot.send_message(message.from_user.id, 'Введите дату, время и сообщение')
    else:
        date_time_str = message_parts[1] + ' ' + message_parts[2]
        send = send_notification(' '.join(message_parts[3:]), date_time_str)
        if (send):
            bot.send_message(message.from_user.id, 'Уведомление установлено')
        else:
            bot.send_message(message.from_user.id, 'Неверный формат даты или времени')



if __name__ == '__main__':
    main()