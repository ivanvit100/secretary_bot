import libs.menu
from i18n import _
import logging

def register_keyboard(bot, check_function):

    @bot.message_handler(func=lambda message: message.text == _("keyboard_files") and check_function(message.from_user.id))
    def keyboard_files_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_files(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_email") and check_function(message.from_user.id))
    def keyboard_email_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_email(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_balance") and check_function(message.from_user.id))
    def keyboard_balance_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_balance(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_tasks") and check_function(message.from_user.id))
    def keyboard_tasks_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_tasks(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_notifications") and check_function(message.from_user.id))
    def keyboard_notifications_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_notifications(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_vps") and check_function(message.from_user.id))
    def keyboard_vps_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_vps(message, bot)
        
    @bot.message_handler(func=lambda message: message.text == _("keyboard_menu") and check_function(message.from_user.id))
    def keyboard_menu_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_menu(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_help") and check_function(message.from_user.id))
    def keyboard_help_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        libs.menu.handle_keyboard_help(message, bot)

    @bot.message_handler(func=lambda message: message.text == _("keyboard_hide") and check_function(message.from_user.id))
    def keyboard_hide_handler(message):
        libs.menu.hide_keyboard(message, bot)
        
    logging.info("All keyboard handlers registered successfully")