import telebot
import logging
import json
import os
import math
from telebot import types
from i18n import _

FILE_PATH = f'{os.path.dirname(os.path.dirname(__file__))}/data/tasks.json'

task_states = {}

class TaskStates:
    IDLE = 0
    WAITING_FOR_TITLE = 1
    WAITING_FOR_DESCRIPTION = 2
    CONFIRMATION = 3

class TaskData:
    def __init__(self):
        self.title = None
        self.description = None
        self.orig_message_id = None

def read_json():
    try:
        with open(FILE_PATH, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f'Error reading tasks: {e}')
        return {"tasks": [], "complete": 0}

def tasks_list(message: telebot.types.Message, bot: telebot.TeleBot, page: int = 0):
    data = read_json()
    tasks = data.get('tasks', [])
    
    if not tasks:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(
            _('task_button_add'), 
            callback_data="task_add"
        ))
        
        bot.send_message(
            message.from_user.id, 
            _('task_none'),
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return

    tasks_per_page = 8
    total_pages = max(1, math.ceil(len(tasks) / tasks_per_page))
    
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * tasks_per_page
    end_idx = min(start_idx + tasks_per_page, len(tasks))
    current_page_tasks = tasks[start_idx:end_idx]

    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for idx, task in enumerate(current_page_tasks):
        absolute_idx = start_idx + idx
        button_text = f"📝 {task['title']}"
        markup.add(types.InlineKeyboardButton(
            button_text, 
            callback_data=f"task_view_{absolute_idx}"
        ))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            _('prev_page'), 
            callback_data=f"task_page_{page-1}"
        ))
    
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton(
            _('next_page'),
            callback_data=f"task_page_{page+1}"
        ))
    
    markup.add(types.InlineKeyboardButton(
        _('task_button_add'), 
        callback_data="task_add"
    ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    message_text = f'*{_("task_list_title")}*'
    if total_pages > 1:
        message_text += f"\n_{_('page')} {page + 1} {_('of')} {total_pages}_"

    bot.send_message(
        message.from_user.id, 
        message_text, 
        parse_mode='Markdown',
        reply_markup=markup
    )

def edit_tasks_list(message_id: int, chat_id: int, bot: telebot.TeleBot, page: int = 0):
    data = read_json()
    tasks = data.get('tasks', [])
    
    if not tasks:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(
            _('task_button_add'), 
            callback_data="task_add"
        ))
        
        bot.edit_message_text(
            _('task_none'),
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return

    tasks_per_page = 8
    total_pages = max(1, math.ceil(len(tasks) / tasks_per_page))
    
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * tasks_per_page
    end_idx = min(start_idx + tasks_per_page, len(tasks))
    current_page_tasks = tasks[start_idx:end_idx]

    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for idx, task in enumerate(current_page_tasks):
        absolute_idx = start_idx + idx
        button_text = f"📝 {task['title']}"
        markup.add(types.InlineKeyboardButton(
            button_text, 
            callback_data=f"task_view_{absolute_idx}"
        ))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            _('prev_page'), 
            callback_data=f"task_page_{page-1}"
        ))
    
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton(
            _('next_page'),
            callback_data=f"task_page_{page+1}"
        ))
    
    markup.add(types.InlineKeyboardButton(
        _('task_button_add'), 
        callback_data="task_add"
    ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    message_text = f'*{_("task_list_title")}*'
    if total_pages > 1:
        message_text += f"\n_{_('page')} {page + 1} {_('of')} {total_pages}_"

    bot.edit_message_text(
        message_text, 
        chat_id,
        message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

def task_view(call, bot: telebot.TeleBot):
    try:
        data = read_json()
        tasks = data.get('tasks', [])
        task_index = int(call.data.split('_')[2])
        
        if task_index < 0 or task_index >= len(tasks):
            bot.answer_callback_query(call.id, _('task_not_found'))
            return
        
        task = tasks[task_index]
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        markup.add(
            types.InlineKeyboardButton(
                _('task_button_complete'), 
                callback_data=f"task_done_{task_index}"
            ),
            types.InlineKeyboardButton(
                _('task_button_delete'), 
                callback_data=f"task_delete_{task_index}"
            )
        )
        
        markup.add(types.InlineKeyboardButton(
            _('task_button_back'), 
            callback_data="task_list"
        ))
        
        task_text = f"*{task['title']}*\n\n{task['description']}"
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            task_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f'Error in task_view: {e}')
        bot.answer_callback_query(call.id, _('task_error'))

def task_delete_callback(call, bot: telebot.TeleBot):
    try:
        data = read_json()
        tasks = data.get('tasks', [])
        task_index = int(call.data.split('_')[2])
        
        if task_index < 0 or task_index >= len(tasks):
            bot.answer_callback_query(call.id, _('task_not_found'))
            return
        
        task = tasks[task_index]["title"]
        tasks.pop(task_index)
        
        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        bot.answer_callback_query(call.id, _('task_deleted_short'))
        
        if tasks:
            edit_tasks_list(
                call.message.message_id,
                call.message.chat.id,
                bot,
                0
            )
        else:
            edit_tasks_list(
                call.message.message_id,
                call.message.chat.id,
                bot
            )
    except Exception as e:
        logging.error(f'Error in task_delete_callback: {e}')
        bot.answer_callback_query(call.id, _('task_error'))

def task_done_callback(call, bot: telebot.TeleBot):
    try:
        data = read_json()
        tasks = data.get('tasks', [])
        task_index = int(call.data.split('_')[2])
        
        if task_index < 0 or task_index >= len(tasks):
            bot.answer_callback_query(call.id, _('task_not_found'))
            return
        
        task = tasks[task_index]["title"]
        tasks.pop(task_index)
        data["complete"] += 1
        
        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        bot.answer_callback_query(call.id, _('task_completed_short'))
        
        if tasks:
            edit_tasks_list(
                call.message.message_id,
                call.message.chat.id,
                bot,
                0
            )
        else:
            edit_tasks_list(
                call.message.message_id,
                call.message.chat.id,
                bot
            )
    except Exception as e:
        logging.error(f'Error in task_done_callback: {e}')
        bot.answer_callback_query(call.id, _('task_error'))

def task_page_callback(call, bot: telebot.TeleBot):
    try:
        page = int(call.data.split('_')[2])
        edit_tasks_list(call.message.message_id, call.message.chat.id, bot, page)
        bot.answer_callback_query(call.id)
    except Exception as e:
        logging.error(f'Error in task_page_callback: {e}')
        bot.answer_callback_query(call.id, _('task_error'))

def task_list_callback(call, bot: telebot.TeleBot):
    try:
        bot.answer_callback_query(call.id)
        edit_tasks_list(call.message.message_id, call.message.chat.id, bot)
    except Exception as e:
        logging.error(f'Error in task_list_callback: {e}')
        bot.answer_callback_query(call.id, _('task_error'))

def task_delete(message: telebot.types.Message, bot: telebot.TeleBot):
    data = read_json()
    tasks = data.get('tasks', [])
    message_parts = message.text.split(' ')
    if len(message_parts) < 3:
        logging.error('No task index provided')
        bot.send_message(message.from_user.id, _('task_index_required'))
        return

    try:
        task_index = int(message_parts[2])
        if task_index < 0 or task_index >= len(tasks):
            bot.send_message(message.from_user.id, _('task_not_found'))
            return
            
        task = tasks[task_index]["title"]
        tasks.pop(task_index)

        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        bot.send_message(message.from_user.id, _('task_deleted', task=task), parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error deleting task: {e}')
        bot.send_message(message.from_user.id, _('task_error'))

def task_done(message: telebot.types.Message, bot: telebot.TeleBot):
    data = read_json()
    tasks = data.get('tasks', [])
    message_parts = message.text.split('_')
    if len(message_parts) < 3:
        logging.error('No task index provided')
        bot.send_message(message.from_user.id, _('task_index_required'))
        return

    try:
        task_index = int(message_parts[2])
        if task_index < 0 or task_index >= len(tasks):
            bot.send_message(message.from_user.id, _('task_not_found'))
            return
            
        task = tasks[task_index]["title"]
        tasks.pop(task_index)
        data["complete"] += 1

        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        bot.send_message(message.from_user.id, _('task_completed', task=task), parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error completing task: {e}')
        bot.send_message(message.from_user.id, _('task_error'))

def task_add(message: telebot.types.Message, bot: telebot.TeleBot):
    message_parts = message.text.split(' ')
    if len(message_parts) < 3:
        bot.send_message(message.from_user.id, _('task_invalid_format'))
        return

    try:
        data = read_json()
        data["tasks"].append({
            "title": message_parts[1],
            "description": ' '.join(message_parts[2:])
        })

        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        bot.send_message(message.from_user.id, _('task_added'))
    except Exception as e:
        logging.error(f'Error adding task: {e}')
        bot.send_message(message.from_user.id, _('task_error'))

def start_task_add(message_or_call, bot: telebot.TeleBot):
    if isinstance(message_or_call, types.CallbackQuery):
        user_id = message_or_call.from_user.id
        chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(_('task_button_cancel'), callback_data="task_add_cancel"))
        
        sent_msg = bot.edit_message_text(
            _('task_enter_title'),
            chat_id,
            message_or_call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        message_id = message_or_call.message.message_id
    else:
        user_id = message_or_call.from_user.id
        chat_id = message_or_call.chat.id
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(_('task_button_cancel'), callback_data="task_add_cancel"))
        
        sent_msg = bot.send_message(
            chat_id,
            _('task_enter_title'),
            reply_markup=markup,
            parse_mode='Markdown'
        )
        message_id = sent_msg.message_id
    
    task_states[user_id] = {
        'state': TaskStates.WAITING_FOR_TITLE,
        'data': TaskData(),
        'message_id': message_id
    }

def handle_task_title(message, bot: telebot.TeleBot):
    user_id = message.from_user.id
    
    if user_id in task_states and task_states[user_id]['state'] == TaskStates.WAITING_FOR_TITLE:
        task_states[user_id]['data'].title = message.text
        task_states[user_id]['state'] = TaskStates.WAITING_FOR_DESCRIPTION
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(_('task_button_cancel'), callback_data="task_add_cancel"))
        
        bot.delete_message(
            message.chat.id,
            task_states[user_id]['message_id']
        )
        
        sent_msg = bot.send_message(
            message.chat.id,
            _('task_title_selected', title=task_states[user_id]['data'].title) + "\n\n" + _('task_enter_description'),
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        task_states[user_id]['message_id'] = sent_msg.message_id
        bot.delete_message(message.chat.id, message.message_id)

def handle_task_description(message, bot: telebot.TeleBot):
    user_id = message.from_user.id
    
    if user_id in task_states and task_states[user_id]['state'] == TaskStates.WAITING_FOR_DESCRIPTION:
        task_states[user_id]['data'].description = message.text
        task_states[user_id]['state'] = TaskStates.CONFIRMATION
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                _('task_button_confirm'), 
                callback_data="task_add_confirm"
            ),
            types.InlineKeyboardButton(
                _('task_button_cancel'), 
                callback_data="task_add_cancel"
            )
        )
        
        title = task_states[user_id]['data'].title
        description = task_states[user_id]['data'].description
        
        preview_text = (
            f"*{_('task_preview')}*\n\n"
            f"{_('task_preview_title')}: *{title}*\n\n"
            f"{_('task_preview_description')}:\n{description}\n\n"
            f"{_('task_confirm_prompt')}"
        )
        
        bot.delete_message(
            message.chat.id,
            task_states[user_id]['message_id']
        )
        
        sent_msg = bot.send_message(
            message.chat.id,
            preview_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        task_states[user_id]['message_id'] = sent_msg.message_id
        bot.delete_message(message.chat.id, message.message_id)

def handle_task_add_confirm(call, bot: telebot.TeleBot):
    user_id = call.from_user.id
    
    if user_id in task_states and task_states[user_id]['state'] == TaskStates.CONFIRMATION:
        title = task_states[user_id]['data'].title
        description = task_states[user_id]['data'].description
        
        try:
            data = read_json()
            data["tasks"].append({
                "title": title,
                "description": description
            })

            with open(FILE_PATH, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            bot.edit_message_text(
                _('task_added_success'),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            del task_states[user_id]
            bot.answer_callback_query(call.id, _('task_added_short'))
            
        except Exception as e:
            logging.error(f'Error adding task: {e}')
            bot.edit_message_text(
                _('task_error'),
                call.message.chat.id,
                call.message.message_id
            )
            bot.answer_callback_query(call.id, _('task_error'))
            del task_states[user_id]

def handle_task_add_cancel(call, bot: telebot.TeleBot):
    user_id = call.from_user.id
    
    if user_id in task_states:
        del task_states[user_id]
        
    bot.edit_message_text(
        _('task_add_cancelled'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)