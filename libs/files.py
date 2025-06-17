import telebot
import logging
import os
import math
from telebot import types
from i18n import _

def save_doc(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        
        with open(f'files/{message.document.file_name}', 'wb') as new_file:
            new_file.write(file)
        
        logging.info(f"File {message.document.file_name} saved")
        bot.send_message(message.from_user.id, _('file_saved'), parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in save_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))

def download_file(message: telebot.types.Message, bot: telebot.TeleBot, type_flag: bool = 0):
    try:
        # Проверяем, является ли сообщение callback query
        if isinstance(message, types.CallbackQuery):
            # Получаем данные из callback
            parts = message.data.split('_')
            # Исправлено: правильные индексы для разбора callback_data
            type_flag = int(parts[2])  # было неправильно: [1]
            file_index = int(parts[3])  # было неправильно: [2]
            user_id = message.from_user.id
            
            # Получаем имя файла по индексу
            folder = 'files' if type_flag else 'public_files'
            files = sorted(os.listdir(folder))
            
            if file_index < 0 or file_index >= len(files):
                bot.answer_callback_query(message.id, _('file_not_found'))
                return
                
            file_name = files[file_index]
            file_path = f'{folder}/{file_name}'
            
            # Отвечаем на callback
            bot.answer_callback_query(message.id)
        else:
            # Классический вариант с текстовой командой
            file_name = message.text.split(' ')[1]
            file_path = f'{'files' if type_flag else 'public_files'}/{file_name}'
            user_id = message.from_user.id

        # Проверяем существование файла и отправляем его
        if not os.path.exists(file_path):
            if isinstance(message, types.CallbackQuery):
                bot.answer_callback_query(message.id, _('file_not_found'))
            else:
                bot.send_message(user_id, _('file_not_found'))
            return
            
        with open(file_path, 'rb') as file:
            bot.send_document(user_id, file, caption=file_name, timeout=300)
        
        logging.info(f'File {file_name} shared')
    except Exception as e:
        logging.error(f"Error in download_file: {e}")
        user_id = message.from_user.id if isinstance(message, types.CallbackQuery) else message.from_user.id
        bot.send_message(user_id, _('file_error'))

def show_files(message: telebot.types.Message, bot: telebot.TeleBot, type_flag: bool = 0, page: int = 0):
    try:
        # Определяем тип запроса (обычное сообщение или callback query)
        if isinstance(message, types.CallbackQuery):
            # Получаем параметры из callback query
            parts = message.data.split('_')
            type_flag = int(parts[2])
            page = int(parts[3])
            user_id = message.from_user.id
            
            # Отвечаем на callback
            bot.answer_callback_query(message.id)
        else:
            user_id = message.from_user.id

        folder = 'files' if type_flag else 'public_files'
        
        # Получаем и сортируем список файлов
        files = sorted(os.listdir(folder))
        if not files:
            if isinstance(message, types.CallbackQuery):
                bot.edit_message_text(_('files_list_empty'), user_id, message.message.message_id)
            else:
                bot.send_message(user_id, _('files_list_empty'))
            return
        
        # Расчет постраничной навигации
        files_per_page = 8
        total_pages = max(1, math.ceil(len(files) / files_per_page))
        
        # Проверка валидности номера страницы
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
        
        # Получаем файлы для текущей страницы
        start_idx = page * files_per_page
        end_idx = min(start_idx + files_per_page, len(files))
        current_page_files = files[start_idx:end_idx]
        
        # Создаем клавиатуру с кнопками для каждого файла
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для файлов
        for idx, file_name in enumerate(current_page_files):
            absolute_idx = start_idx + idx
            # Обрезаем имя файла, если оно слишком длинное
            display_name = file_name[:40] + '...' if len(file_name) > 40 else file_name
            # Добавляем кнопку для скачивания файла
            download_button = types.InlineKeyboardButton(
                f"📄 {display_name}", 
                callback_data=f"file_download_{1 if type_flag else 0}_{absolute_idx}"
            )
            markup.add(download_button)
        
        # Добавляем кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton(
                "◀️ " + _('prev_page'), 
                callback_data=f"file_page_{1 if type_flag else 0}_{page-1}"
            ))
        
        if page < total_pages - 1:
            nav_buttons.append(types.InlineKeyboardButton(
                _('next_page') + " ▶️", 
                callback_data=f"file_page_{1 if type_flag else 0}_{page+1}"
            ))
        
        # Добавляем кнопки навигации в ряд, если они есть
        if nav_buttons:
            markup.row(*nav_buttons)
        
        # Формируем текст сообщения
        folder_title = _("private_files_title") if type_flag else _("public_files_title")
        message_text = f"*{folder_title}*\n" + \
                      f"_{_('page')} {page + 1} {_('of')} {total_pages}_"
        
        # Отправляем или обновляем сообщение
        if isinstance(message, types.CallbackQuery):
            bot.edit_message_text(
                message_text,
                user_id,
                message.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(
                user_id,
                message_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
    except Exception as e:
        logging.error(f"Error in show_files: {e}")
        user_id = message.from_user.id if isinstance(message, types.CallbackQuery) else message.from_user.id
        bot.send_message(user_id, _('file_error'))

def delete_file(message: telebot.types.Message, bot: telebot.TeleBot, type_flag: bool = 0):
    try:
        file_name = message.text.split(' ')[1]
        file_path = f'{'files' if type_flag else 'public_files'}/{file_name}'
        
        if not os.path.exists(file_path):
            bot.send_message(message.from_user.id, _('file_not_found'))
            return
            
        os.remove(file_path)
        logging.info(f'File {file_name} deleted')
        bot.send_message(message.from_user.id, _('file_deleted'), parse_mode='Markdown')
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
        bot.send_message(message.from_user.id, _('file_shared'), parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in share_file: {e}")
        bot.send_message(message.from_user.id, _('file_error'))