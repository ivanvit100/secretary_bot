import libs.menu
from i18n import _
import logging

def register_keyboard(bot, check_function):
    def check(user_id, module=None):
        return check_function(user_id, module) 

    @bot.message_handler(func=lambda message: message.text == _("keyboard_email") and check(message.from_user.id, "email"))
    def keyboard_email_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_email(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_balance") and check(message.from_user.id, "balance"))
    def keyboard_balance_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_balance(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_tasks") and check(message.from_user.id, "task"))
    def keyboard_tasks_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_tasks(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_notifications") and check(message.from_user.id, "notification"))
    def keyboard_notifications_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_notifications(message, bot)
        
    @bot.message_handler(func=lambda message: message.text == _("keyboard_menu"))
    def keyboard_menu_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.menu(message, bot)
        
    logging.info("All keyboard handlers registered successfully")