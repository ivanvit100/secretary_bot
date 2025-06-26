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
        if isinstance(message, types.CallbackQuery):
            parts = message.data.split('_')
            type_flag = int(parts[2])
            file_index = int(parts[3])
            user_id = message.from_user.id
            
            folder = 'files' if type_flag else 'public_files'
            files = sorted(os.listdir(folder))
            
            if file_index < 0 or file_index >= len(files):
                bot.answer_callback_query(message.id, _('file_not_found'))
                return
                
            file_name = files[file_index]
            file_path = f'{folder}/{file_name}'
            
            bot.answer_callback_query(message.id)
        else:
            file_name = message.text.split(' ')[1]
            file_path = f'{'files' if type_flag else 'public_files'}/{file_name}'
            user_id = message.from_user.id

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
        if isinstance(message, types.CallbackQuery):
            parts = message.data.split('_')
            type_flag = int(parts[2])
            page = int(parts[3])
            user_id = message.from_user.id
            
            bot.answer_callback_query(message.id)
        else:
            user_id = message.from_user.id

        folder = 'files' if type_flag else 'public_files'
        
        files = sorted(os.listdir(folder))
        if not files:
            if isinstance(message, types.CallbackQuery):
                bot.edit_message_text(_('files_list_empty'), user_id, message.message.message_id)
            else:
                bot.send_message(user_id, _('files_list_empty'))
            return
        
        files_per_page = 8
        total_pages = max(1, math.ceil(len(files) / files_per_page))
        
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
        
        start_idx = page * files_per_page
        end_idx = min(start_idx + files_per_page, len(files))
        current_page_files = files[start_idx:end_idx]
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, file_name in enumerate(current_page_files):
            absolute_idx = start_idx + idx
            display_name = file_name[:40] + '...' if len(file_name) > 40 else file_name
            download_button = types.InlineKeyboardButton(
                f"📄 {display_name}", 
                callback_data=f"file_download_{1 if type_flag else 0}_{absolute_idx}"
            )
            markup.add(download_button)
        
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
        
        if nav_buttons:
            markup.row(*nav_buttons)
        
        folder_title = _("private_files_title") if type_flag else _("public_files_title")
        message_text = f"*{folder_title}*\n" + \
                      f"_{_('page')} {page + 1} {_('of')} {total_pages}_"
        
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

def delete_files_menu(message: telebot.types.Message, bot: telebot.TeleBot, type_flag: bool = 0, page: int = 0):
    try:
        if isinstance(message, types.CallbackQuery):
            parts = message.data.split('_')
            
            if len(parts) >= 4 and parts[1] == "deletepage":
                try:
                    type_flag = int(parts[2])
                    page = int(parts[3])
                except ValueError:
                    logging.warning(f"Invalid format in callback_data: {message.data}")
            
            elif message.data == "menu_files_delete_private":
                type_flag = 1
                page = 0
            elif message.data == "menu_files_delete_public":
                type_flag = 0
                page = 0
                
            user_id = message.from_user.id
            bot.answer_callback_query(message.id)
        else:
            user_id = message.from_user.id

        folder = 'files' if type_flag else 'public_files'
        files = sorted(os.listdir(folder))
        if not files:
            if isinstance(message, types.CallbackQuery):
                bot.edit_message_text(_('files_list_empty'), user_id, message.message.message_id)
            else:
                bot.send_message(user_id, _('files_list_empty'))
            return
        
        files_per_page = 8
        total_pages = max(1, math.ceil(len(files) / files_per_page))
        
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
        
        start_idx = page * files_per_page
        end_idx = min(start_idx + files_per_page, len(files))
        current_page_files = files[start_idx:end_idx]
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, file_name in enumerate(current_page_files):
            absolute_idx = start_idx + idx
            display_name = file_name[:40] + '...' if len(file_name) > 40 else file_name
            delete_button = types.InlineKeyboardButton(
                f"🗑️ {display_name}", 
                callback_data=f"file_delete_{1 if type_flag else 0}_{absolute_idx}"
            )
            markup.add(delete_button)
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton(
                "◀️ " + _('prev_page'), 
                callback_data=f"file_deletepage_{1 if type_flag else 0}_{page-1}"
            ))
        
        if page < total_pages - 1:
            nav_buttons.append(types.InlineKeyboardButton(
                _('next_page') + " ▶️", 
                callback_data=f"file_deletepage_{1 if type_flag else 0}_{page+1}"
            ))
        
        markup.add(types.InlineKeyboardButton(
            "🔙 " + _('back_to_menu'),
            callback_data="menu_files"
        ))
        
        if nav_buttons:
            markup.row(*nav_buttons)
        
        folder_title = _("delete_private_files_title") if type_flag else _("delete_public_files_title")
        message_text = f"*{folder_title}*\n" + \
                      f"_{_('page')} {page + 1} {_('of')} {total_pages}_"
        
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
        logging.error(f"Error in delete_files_menu: {e}")
        user_id = message.from_user.id if isinstance(message, types.CallbackQuery) else message.from_user.id
        bot.send_message(user_id, _('file_error'))

def delete_file_by_callback(call: types.CallbackQuery, bot: telebot.TeleBot):
    try:
        parts = call.data.split('_')
        type_flag = int(parts[2])
        file_index = int(parts[3])
        user_id = call.from_user.id
        
        folder = 'files' if type_flag else 'public_files'
        files = sorted(os.listdir(folder))
        
        if file_index < 0 or file_index >= len(files):
            bot.answer_callback_query(call.id, _('file_not_found'))
            return
            
        file_name = files[file_index]
        file_path = f'{folder}/{file_name}'
        
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, _('file_not_found'))
            return
            
        os.remove(file_path)
        logging.info(f'File {file_name} deleted via menu')
        
        bot.answer_callback_query(call.id, text=_('file_deleted_notification'))
        
        current_page = file_index // 8
        delete_files_menu(call, bot, type_flag, current_page)
        
    except Exception as e:
        logging.error(f"Error in delete_file_by_callback: {e}")
        bot.answer_callback_query(call.id, text=_('file_error'))
        bot.send_message(call.from_user.id, _('file_error'))

def delete_file(message: telebot.types.Message, bot: telebot.TeleBot, type_flag: bool = 0):
    try:
        if len(message.text.split(' ')) > 1:
            file_name = message.text.split(' ')[1]
            folder = 'files' if type_flag else 'public_files'
            file_path = f'{folder}/{file_name}'
            
            if not os.path.exists(file_path):
                bot.send_message(message.from_user.id, _('file_not_found'))
                return
            
            os.remove(file_path)
            logging.info(f'File {file_name} deleted')
            bot.send_message(message.from_user.id, _('file_deleted'))
        else:
            delete_files_menu(message, bot, type_flag)
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

def share_files_menu(message: telebot.types.Message, bot: telebot.TeleBot, page: int = 0):
    try:
        if isinstance(message, types.CallbackQuery):
            parts = message.data.split('_')
            
            if len(parts) >= 3 and parts[1] == "sharepage":
                try:
                    page = int(parts[2])
                except ValueError:
                    logging.warning(f"Invalid format in callback_data: {message.data}")
            
            user_id = message.from_user.id
            bot.answer_callback_query(message.id)
        else:
            user_id = message.from_user.id

        private_files = [(f, True) for f in sorted(os.listdir('files'))]
        public_files = [(f, False) for f in sorted(os.listdir('public_files'))]
        
        all_files = private_files + public_files
        all_files.sort(key=lambda x: x[0])
        
        if not all_files:
            if isinstance(message, types.CallbackQuery):
                bot.edit_message_text(_('files_list_empty'), user_id, message.message.message_id)
            else:
                bot.send_message(user_id, _('files_list_empty'))
            return
        
        files_per_page = 8
        total_pages = max(1, math.ceil(len(all_files) / files_per_page))
        
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
        
        start_idx = page * files_per_page
        end_idx = min(start_idx + files_per_page, len(all_files))
        current_page_files = all_files[start_idx:end_idx]
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, (file_name, is_private) in enumerate(current_page_files):
            absolute_idx = start_idx + idx
            icon = "🔒" if is_private else "🌐"
            display_name = file_name[:40] + '...' if len(file_name) > 40 else file_name
            
            share_button = types.InlineKeyboardButton(
                f"{icon} {display_name}", 
                callback_data=f"file_share_{1 if is_private else 0}_{absolute_idx}"
            )
            markup.add(share_button)
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton(
                "◀️ " + _('prev_page'), 
                callback_data=f"file_sharepage_{page-1}"
            ))
        
        if page < total_pages - 1:
            nav_buttons.append(types.InlineKeyboardButton(
                _('next_page') + " ▶️", 
                callback_data=f"file_sharepage_{page+1}"
            ))
        
        markup.add(types.InlineKeyboardButton(
            "🔙 " + _('back_to_menu'),
            callback_data="menu_files"
        ))
        
        if nav_buttons:
            markup.row(*nav_buttons)
        
        message_text = f"*{_('share_files_title')}*\n" + \
                       f"_{_('page')} {page + 1} {_('of')} {total_pages}_"
        
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
        logging.error(f"Error in share_files_menu: {e}")
        user_id = message.from_user.id if isinstance(message, types.CallbackQuery) else message.from_user.id
        bot.send_message(user_id, _('file_error'))

def share_file_by_callback(call: types.CallbackQuery, bot: telebot.TeleBot):
    try:
        parts = call.data.split('_')
        is_private = int(parts[2])
        file_index = int(parts[3])
        user_id = call.from_user.id
        
        private_files = [(f, True) for f in sorted(os.listdir('files'))]
        public_files = [(f, False) for f in sorted(os.listdir('public_files'))]
        all_files = private_files + public_files
        all_files.sort(key=lambda x: x[0])
        
        if file_index < 0 or file_index >= len(all_files):
            bot.answer_callback_query(call.id, _('file_not_found'))
            return
            
        file_name, is_file_private = all_files[file_index]
        src_path = f"{'files' if is_file_private else 'public_files'}/{file_name}"
        dest_path = f"{'public_files' if is_file_private else 'files'}/{file_name}"
        
        if not os.path.exists(src_path):
            bot.answer_callback_query(call.id, _('file_not_found'))
            return
        
        os.rename(src_path, dest_path)
        logging.info(f"File {file_name} moved from {'private' if is_file_private else 'public'} to {'public' if is_file_private else 'private'}")
        
        bot.answer_callback_query(call.id, text=_('file_moved_notification'))
        
        current_page = file_index // 8
        share_files_menu(call, bot, current_page)
        
    except Exception as e:
        logging.error(f"Error in share_file_by_callback: {e}")
        bot.answer_callback_query(call.id, text=_('file_error'))
        bot.send_message(call.from_user.id, _('file_error'))