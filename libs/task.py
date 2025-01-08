import telebot
import logging
import json
import os

FILE_PATH = f'{os.path.dirname(os.path.dirname(__file__))}/data/tasks.json'

def read_json():
    try:
        with open(FILE_PATH, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f'Error reading tasks: {e}')
        return []

def tasks_list(message: telebot.types.Message, bot: telebot.TeleBot):
    tasks = read_json()
    if not tasks:
        bot.send_message(message.from_user.id, 'У вас нет задач')
        return

    tasks_list = ""
    for index, task in enumerate(tasks):
        tasks_list += f"__{task['tasks']['title']}__\n{task['tasks']['description']}Выполнить: /task\_done\_{index}\n\n"

    bot.send_message(message.from_user.id, f'*Список задач*\n\n{tasks_list}', parse_mode='Markdown')

def task_done(message: telebot.types.Message, bot: telebot.TeleBot):
    tasks = read_json()
    message_parts = message.text.split('_')
    if len(message_parts) < 3:
        logging.error('No task index provided')
        bot.send_message(message.from_user.id, 'Произошла ошибка')
        return

    try:
        task_index = int(message_parts[2])
        task = tasks["tasks"][task_index]["title"]
        tasks.pop(task_index)
        tasks["complete"] += 1;

        with open(FILE_PATH, 'w') as file:
            json.dump(tasks, file, indent=4)

        bot.send_message(message.from_user.id, f'Задача `{task}` выполнена', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.from_user.id, 'Произошла ошибка')

def task_add(message: telebot.types.Message, bot: telebot.TeleBot):
    message_parts = message.text.split(' ')
    if len(message_parts) < 3:
        bot.send_message(message.from_user.id, 'Некорректный формат ввода')
        return

    tasks = read_json()
    tasks["tasks"].append({
        "title": ' '.join(message_parts[1]),
        "description": ' '.join(message_parts[2:])
    })

    with open(FILE_PATH, 'w') as file:
        json.dump(tasks, file, indent=4)

    bot.send_message(message.from_user.id, 'Задача добавлена')