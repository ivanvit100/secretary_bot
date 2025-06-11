import shlex
import telebot
import logging
import datetime
import subprocess
from i18n import _

def ssh(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        message_parts = shlex.split(message.text)
        command = message_parts[1]
        params = [part for part in message_parts[2:] if not part.startswith('-')]
        flags = [part for part in message_parts[2:] if part.startswith('-')]

        if 'sudo' in message_parts:
            logging.warning(f'User {message.from_user.id} tried to use sudo')
            bot.send_message(message.from_user.id, _("ssh_sudo_forbidden"))
            return

        result = subprocess.run([command] + params + flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            bot.send_message(message.from_user.id, _("ssh_command_result", stdout=result.stdout), parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, _("ssh_command_error", stderr=result.stderr), parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.from_user.id, _("ssh_error"))
        logging.error(f'Error in ssh: {e}')

def get_log(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        with open('./secretary.log', 'r') as file:
            lines = file.readlines()
            log = ''.join(lines[-25:])
        bot.send_message(message.from_user.id, f"{_('log_header')}\n\n{log}")
    except Exception as e:
        logging.error(f'Error in get_log: {e}')
        bot.send_message(message.from_user.id, _("ssh_error"))

def clean_logs():
    try:
        log_file_path = './secretary.log'
        with open(log_file_path, 'r') as file:
            lines = file.readlines()

        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        filtered_lines = []

        for line in lines:
            try:
                log_date_str = line.split(' ')[0]
                log_date = datetime.datetime.strptime(log_date_str, '%Y-%m-%d')
                if log_date >= three_days_ago:
                    filtered_lines.append(line)
            except ValueError:
                continue

        with open(log_file_path, 'w') as file:
            file.writelines(filtered_lines)
            
        logging.info(_("log_cleaned"))
    except Exception as e:
        logging.error(f'Error in clean_logs: {e}')