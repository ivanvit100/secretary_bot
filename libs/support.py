import shlex
import telebot
import subprocess
import logging

def ssh(message: telebot.types.Message, bot: telebot.TeleBot):
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

def get_log(message: telebot.types.Message, bot: telebot.TeleBot):
    with open('./secretary.log', 'r') as file:
        lines = file.readlines()
        log = ''.join(lines[-25:])
    bot.send_message(message.from_user.id, log)