import os
import config
from dotenv import load_dotenv, find_dotenv, set_key
from i18n import _

USER_PREFIX = "USER_"
PERM_PREFIX = "PERM_"
USER_ID = os.getenv('USER_ID')

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

def list_users(admin_id, bot):
    admin_id = str(admin_id)
    
    if admin_id != USER_ID:
        bot.send_message(admin_id, _('admin_required'))
        return False
    
    message = _('users_list_title') + "\n\n"
    message += f"👤 *{_('main_admin')}* (ID: `{USER_ID}`)\n\n"
    
    users = {}
    for key, value in os.environ.items():
        if key.startswith(USER_PREFIX) and key != f"USER_ID":
            user_id = key[len(USER_PREFIX):]
            name = value
            users[user_id] = {"name": name, "permissions": {}}
    
    for key, value in os.environ.items():
        if key.startswith(PERM_PREFIX):
            parts = key[len(PERM_PREFIX):].split("_", 1)
            if len(parts) == 2:
                user_id, module = parts
                if user_id in users and module in config.MODULES and value == "1":
                    users[user_id]["permissions"][module] = True
    
    for user_id, user_data in users.items():
        message += f"👤 *{user_data['name']}* (ID: `{user_id}`)\n"
        message += _('permissions') + ":\n"
        
        for module in config.MODULES:
            if config.MODULES[module]:
                enabled = module in user_data.get("permissions", {})
                module_name = _(f'module_{module}')
                status = '✅' if enabled else '❌'
                message += f"  - {module_name}: {status}\n"
        
        message += "\n"
    
    bot.send_message(admin_id, message, parse_mode="Markdown")
    return True