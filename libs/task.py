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
    data = read_json()
    tasks = data.get('tasks', [])
    if not tasks:
        bot.send_message(message.from_user.id, 'У вас нет задач')
        return

    tasks_list = ""
    for index, task in enumerate(tasks):
        tasks_list += f"__{task['title']}__\n{task['description']}\nВыполнить: /task\_done\_{index}\n\n"

    bot.send_message(message.from_user.id, f'*Список задач*\n\n{tasks_list}', parse_mode='Markdown')

def task_delete(message: telebot.types.Message, bot: telebot.TeleBot):
    data = read_json()
    tasks = data.get('tasks', [])
    message_parts = message.text.split(' ')
    if len(message_parts) < 3:
        logging.error('No task index provided')
        bot.send_message(message.from_user.id, 'Произошла ошибка')
        return

    try:
        task_index = int(message_parts[2])
        task = tasks[task_index]["title"]
        tasks.pop(task_index)

        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        bot.send_message(message.from_user.id, f'Задача `{task}` удалена', parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error completing task: {e}')
        bot.send_message(message.from_user.id, 'Произошла ошибка')

def task_done(message: telebot.types.Message, bot: telebot.TeleBot):
    data = read_json()
    tasks = data.get('tasks', [])
    message_parts = message.text.split('_')
    if len(message_parts) < 3:
        logging.error('No task index provided')
        bot.send_message(message.from_user.id, 'Произошла ошибка')
        return

    try:
        task_index = int(message_parts[2])
        task = tasks[task_index]["title"]
        tasks.pop(task_index)
        data["complete"] += 1

        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        bot.send_message(message.from_user.id, f'Задача `{task}` выполнена', parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error completing task: {e}')
        bot.send_message(message.from_user.id, 'Произошла ошибка')

def task_add(message: telebot.types.Message, bot: telebot.TeleBot):
    message_parts = message.text.split(' ')
    if len(message_parts) < 3:
        bot.send_message(message.from_user.id, 'Некорректный формат ввода')
        return

    data = read_json()
    data["tasks"].append({
        "title": message_parts[1],
        "description": ' '.join(message_parts[2:])
    })

    with open(FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    bot.send_message(message.from_user.id, 'Задача добавлена')