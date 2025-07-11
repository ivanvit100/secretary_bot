import os
import math
import time
import config
import logging
from dotenv import load_dotenv, find_dotenv, set_key
from telebot import types
from i18n import _

USER_PREFIX = "USER_"
PERM_PREFIX = "PERM_"
USER_ID = os.getenv('USER_ID')

add_user_states = {}

class AddUserState:
    WAITING_FOR_ID = 1
    WAITING_FOR_NAME = 2

def check_permission(user_id, bot, module=None, silent=False):
    user_id = str(user_id)
    USER_ID = os.getenv('USER_ID')
    
    if user_id == USER_ID:
        return True
    if not os.getenv(f"{USER_PREFIX}{user_id}"):
        if not silent:
            bot.send_message(user_id, _('no_permission'))
        return False
    if module is None:
        return True
    if os.getenv(f"{PERM_PREFIX}{user_id}_{module}") == "1":
        return True
        
    if not silent:
        bot.send_message(user_id, _('no_permission_module', module=_(f'module_{module}')))
    return False

def load_user_env():
    load_dotenv(find_dotenv(), override=True)

def check(user_id, bot, module=None):
    user_id = str(user_id)
    
    if user_id == USER_ID:
        return True
    if not os.getenv(f"{USER_PREFIX}{user_id}"):
        bot.send_message(user_id, _('no_permission'))
        return False
    if module is None:
        return True
    if os.getenv(f"{PERM_PREFIX}{user_id}_{module}") == "1":
        return True
        
    bot.send_message(user_id, _('no_permission_module', module=_(f'module_{module}')))
    return False

def add_user(admin_id, user_id, name, bot):
    admin_id = str(admin_id)
    user_id = str(user_id)
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
        
    dotenv_path = find_dotenv()
    set_key(dotenv_path, f"{USER_PREFIX}{user_id}", name)
    
    bot.send_message(admin_id, _('user_added', user_id=user_id, name=name))
    load_user_env()
    return True

def remove_user(admin_id, user_id, bot):
    admin_id = str(admin_id)
    user_id = str(user_id)
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
        
    name = os.getenv(f"{USER_PREFIX}{user_id}")
    if not name:
        bot.send_message(admin_id, _('user_not_found', user_id=user_id))
        return False
    
    dotenv_path = find_dotenv()
    
    with open(dotenv_path, 'r') as file:
        lines = file.readlines()
        
    new_lines = []
    for line in lines:
        if not line.startswith(f"{USER_PREFIX}{user_id}=") and \
           not line.startswith(f"{PERM_PREFIX}{user_id}_"):
            new_lines.append(line)
            
    with open(dotenv_path, 'w') as file:
        file.writelines(new_lines)
        
    bot.send_message(admin_id, _('user_removed', user_id=user_id, name=name))
    load_user_env()
    return True

def set_permission(admin_id, user_id, module, value, bot):
    admin_id = str(admin_id)
    user_id = str(user_id)
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
        
    name = os.getenv(f"{USER_PREFIX}{user_id}")
    if not name:
        bot.send_message(admin_id, _('user_not_found', user_id=user_id))
        return False
    if module not in config.MODULES:
        bot.send_message(admin_id, _('module_not_found', module=module))
        return False
        
    dotenv_path = find_dotenv()
    set_key(dotenv_path, f"{PERM_PREFIX}{user_id}_{module}", "1" if value else "0")
    
    status = _('enabled') if value else _('disabled')
    bot.send_message(admin_id, _('permission_updated', user=name, user_id=user_id, 
                                module=_(f'module_{module}'), status=status))
    load_user_env()
    return True

def list_users(admin_id, bot, page=0, call=None):
    admin_id = str(admin_id)
    USER_ID = os.getenv('USER_ID')
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
    
    users = []
    for key, value in os.environ.items():
        if key.startswith(USER_PREFIX) and key != "USER_ID":
            user_id = key[len(USER_PREFIX):]
            name = value
            users.append({"id": user_id, "name": name})
    
    message = f"*{_('admin_info')}*\n"
    message += f"ID: `{USER_ID}`\n\n"
    message += f"*{_('users_list_title')}*\n"
    
    if not users:
        message += _('no_users_found') + "\n"
    
    users_per_page = 8
    total_pages = max(1, math.ceil(len(users) / users_per_page))
    
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_idx = page * users_per_page
    end_idx = min(start_idx + users_per_page, len(users))
    
    for i in range(start_idx, end_idx):
        user = users[i]
        markup.add(types.InlineKeyboardButton(
            f"👤 {user['name']}", 
            callback_data=f"user_info_{user['id']}"
        ))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            _('prev_page'), 
            callback_data=f"users_page_{page-1}"
        ))
    
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton(
            _('next_page'),
            callback_data=f"users_page_{page+1}"
        ))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.add(types.InlineKeyboardButton(_("add_new_user"), callback_data="add_new_user"))
    markup.add(types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main"))
    
    if total_pages > 1:
        message += f"\n_{_('page')} {page + 1} {_('of')} {total_pages}_"
    
    if call:
        try:
            bot.edit_message_text(
                message,
                chat_id=int(admin_id),
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            return True
        except Exception as e:
            logging.error(f"Error editing message: {e}")
    
    try:
        bot.send_message(
            admin_id, 
            message, 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        return True
    except Exception as e:
        logging.error(f"Error sending users list: {e}")
        return False

def show_user_info(admin_id, user_id, bot):
    admin_id = str(admin_id)
    USER_ID = os.getenv('USER_ID')
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
    
    name = os.getenv(f"{USER_PREFIX}{user_id}")
    if not name:
        bot.send_message(admin_id, _('user_not_found', user_id=user_id))
        return False
    
    message = f"*{_('user_info')}*\n"
    message += f"{_('name')}: {name}\n"
    message += f"ID: `{user_id}`\n\n"
    
    try:
        user_info = bot.get_chat(user_id)
        
        if user_info.first_name:
            message += f"{_('telegram_first_name')}: {user_info.first_name}\n"
        if hasattr(user_info, 'last_name') and user_info.last_name:
            message += f"{_('telegram_last_name')}: {user_info.last_name}\n"
        if hasattr(user_info, 'username') and user_info.username:
            message += f"{_('telegram_username')}: @{user_info.username}\n"
            message += f"{_('telegram_link')}: https://t.me/{user_info.username}\n"
        else:
            message += f"{_('telegram_link')}: tg://user?id={user_id}\n"
        
        if hasattr(user_info, 'bio') and user_info.bio:
            message += f"{_('telegram_bio')}: {user_info.bio}\n"
        if hasattr(user_info, 'language_code') and user_info.language_code:
            message += f"{_('telegram_language')}: {user_info.language_code}\n"
        if hasattr(user_info, 'is_premium') and user_info.is_premium:
            message += f"Telegram Premium: ✅\n"
            
    except Exception as e:
        logging.warning(f"Could not get additional Telegram info for user {user_id}: {e}")
        pass
    
    message += f"\n*{_('permissions')}:*\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    modules = [
        ("balance", _("module_balance")),
        ("notification", _("module_notification")),
        ("task", _("module_task")),
        ("email", _("module_email")),
        ("files", _("module_files")),
        ("vps", _("module_vps"))
    ]
    
    for module_code, module_name in modules:
        if not config.MODULES[module_code]:
            continue
        
        has_permission = os.getenv(f"{PERM_PREFIX}{user_id}_{module_code}") == "1"
        
        status = "✅" if has_permission else "❌"
        markup.add(types.InlineKeyboardButton(
            f"{status} {module_name}",
            callback_data=f"toggle_perm_{user_id}_{module_code}_{0 if has_permission else 1}"
        ))
    
    markup.add(types.InlineKeyboardButton(
        _("back_to_users"),
        callback_data="menu_permissions"
    ))
    
    bot.send_message(admin_id, message, parse_mode="Markdown", reply_markup=markup)
    return True

def toggle_permission(admin_id, user_id, module, new_state, bot):
    admin_id = str(admin_id)
    USER_ID = os.getenv('USER_ID')
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
    
    name = os.getenv(f"{USER_PREFIX}{user_id}")
    if not name:
        bot.send_message(admin_id, _('user_not_found', user_id=user_id))
        return False
    
    dotenv_path = find_dotenv()
    set_key(dotenv_path, f"{PERM_PREFIX}{user_id}_{module}", "1" if new_state else "0")
    
    load_dotenv(find_dotenv(), override=True)
    return show_user_info(admin_id, user_id, bot)

def start_add_user(call, bot):
    admin_id = call.from_user.id
    USER_ID = os.getenv('USER_ID')
    
    if str(admin_id) != USER_ID:
        bot.answer_callback_query(call.id, _('admin_required'))
        return False
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user'))
    
    msg = bot.edit_message_text(
        _('enter_user_id'),
        call.message.chat.id, 
        call.message.message_id,
        reply_markup=markup
    )
    
    add_user_states[admin_id] = {
        'state': AddUserState.WAITING_FOR_ID,
        'message_id': msg.message_id
    }
    return True

def handle_add_user_id(message, bot):
    admin_id = message.from_user.id
    
    if admin_id not in add_user_states:
        return False
    
    bot.delete_message(message.chat.id, message.message_id)
    
    user_id = message.text.strip()
    try:
        int(user_id)
    except ValueError:
        bot.edit_message_text(
            _('invalid_user_id'),
            message.chat.id,
            add_user_states[admin_id]['message_id'],
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(_('try_again'), callback_data='add_new_user'),
                types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user')
            )
        )
        return False
    
    if os.getenv(f"{USER_PREFIX}{user_id}"):
        bot.edit_message_text(
            _('user_already_exists'),
            message.chat.id,
            add_user_states[admin_id]['message_id'],
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(_('try_again'), callback_data='add_new_user'),
                types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user')
            )
        )
        return False
    
    add_user_states[admin_id]['user_id'] = user_id
    add_user_states[admin_id]['state'] = AddUserState.WAITING_FOR_NAME
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user'))
    
    bot.edit_message_text(
        _('enter_user_name'),
        message.chat.id,
        add_user_states[admin_id]['message_id'],
        reply_markup=markup
    )
    return True

def handle_add_user_name(message, bot):
    admin_id = message.from_user.id
    
    if admin_id not in add_user_states or add_user_states[admin_id]['state'] != AddUserState.WAITING_FOR_NAME:
        return False
    
    bot.delete_message(message.chat.id, message.message_id)
    
    name = message.text.strip()
    if not name:
        bot.edit_message_text(
            _('invalid_user_name'),
            message.chat.id,
            add_user_states[admin_id]['message_id'],
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(_('try_again'), callback_data='add_new_user'),
                types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user')
            )
        )
        return False
    
    add_user_states[admin_id]['name'] = name
    user_id = add_user_states[admin_id]['user_id']
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(_('confirm'), callback_data=f'confirm_add_user_{user_id}_{name}'),
        types.InlineKeyboardButton(_('cancel'), callback_data='cancel_add_user')
    )
    
    bot.edit_message_text(
        _('confirm_add_user', user_id=user_id, name=name),
        message.chat.id,
        add_user_states[admin_id]['message_id'],
        reply_markup=markup,
        parse_mode='Markdown'
    )
    return True

def confirm_add_user(call, bot):
    admin_id = call.from_user.id
    USER_ID = os.getenv('USER_ID')
    
    if str(admin_id) != USER_ID:
        bot.answer_callback_query(call.id, _('admin_required'))
        return False
    
    parts = call.data.split('_')
    user_id = parts[3]
    name = parts[4]
    
    if admin_id in add_user_states and 'name' in add_user_states[admin_id]:
        name = add_user_states[admin_id]['name']
    
    try:
        dotenv_path = find_dotenv()
        set_key(dotenv_path, f"{USER_PREFIX}{user_id}", name)
        
        modules = ["balance", "notification", "task", "email", "files", "vps"]
        for module in modules:
            set_key(dotenv_path, f"{PERM_PREFIX}{user_id}_{module}", "0")
        
        load_dotenv(dotenv_path, override=True)
        
        if admin_id in add_user_states:
            del add_user_states[admin_id]
        
        bot.edit_message_text(
            _('user_added_success', user_id=user_id, name=name),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        time.sleep(1)
        list_users(admin_id, bot, 0)
        return True
        
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        bot.edit_message_text(
            _('error_adding_user', error=str(e)),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(_('back_to_users'), callback_data='menu_permissions')
            )
        )
        return False

def cancel_add_user(call, bot):
    admin_id = call.from_user.id
    
    if admin_id in add_user_states:
        del add_user_states[admin_id]
    
    list_users(admin_id, bot, 0, call)
    return True