import telebot
import logging
import os
from i18n import _

def save_doc(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        
        with open(f'files/{message.document.file_name}', 'wb') as new_file:
            new_file.write(file)
        
        logging.info(f"File {message.document.file_name} saved")
        bot.send_message(message.from_user.id, _('file_saved'))
    except Exception as e:
        logging.error(f"Error in save_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))

def download_file(message: telebot.types.Message, bot: telebot.TeleBot, type: bool = 0):
    try:
        file_name = message.text.split(' ')[1]
        file_path = f'{'files' if type else 'public_files'}/{file_name}'
        
        if not os.path.exists(file_path):
            bot.send_message(message.from_user.id, _('file_not_found'))
            return
            
        with open(file_path, 'rb') as file:
            bot.send_document(message.from_user.id, file, timeout=300)
        logging.info(f'File {file_name} shared')
    except Exception as e:
        logging.error(f"Error in share_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))

def show_files(message: telebot.types.Message, bot: telebot.TeleBot, type: bool = 0):
    try:
        files = os.listdir('files' if type else 'public_files')
        if not files:
            bot.send_message(message.from_user.id, _('files_list_empty'))
            return
            
        files_list = '\n'.join(files)
        bot.send_message(message.from_user.id, f'*{_("files_list_title")}*\n\n`{files_list}`', parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in list_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))

def delete_file(message: telebot.types.Message, bot: telebot.TeleBot, type: bool = 0):
    try:
        file_name = message.text.split(' ')[1]
        file_path = f'{'files' if type else 'public_files'}/{file_name}'
        
        if not os.path.exists(file_path):
            bot.send_message(message.from_user.id, _('file_not_found'))
            return
            
        os.remove(file_path)
        logging.info(f'File {file_name} deleted')
        bot.send_message(message.from_user.id, _('file_deleted'))
    except Exception as e:
        logging.error(f"Error in delete_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))

def share_file(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        file_name = message.text.split(' ')[1]
        src_path = f'files/{file_name}'
        dest_path = f'public_files/{file_name}'
        
        if not os.path.exists(src_path):
            bot.send_message(message.from_user.id, _('file_not_found'))
            return
            
        os.rename(src_path, dest_path)
        logging.info(f'File {file_name} moved to public_files')
        bot.send_message(message.from_user.id, _('file_shared'))
    except Exception as e:
        logging.error(f"Error in share_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))