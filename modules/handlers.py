import os
import libs
import config
import telebot
import logging
from i18n import _
from libs.support import get_log
from libs.notification import user_states, NotificationStates

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

#########################
#                       #
#        COMMANDS       #
#                       #
#########################

def register_handlers(bot, check_function):
    
    def check(user_id):
        return check_function(user_id)
    
    @bot.message_handler(func=lambda message: message.from_user.id in libs.menu.ssh_mode_users)
    def ssh_mode_message_handler(message):
        libs.menu.process_ssh_message(message, bot)

    @bot.message_handler(commands=['start'])
    def start(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.from_user.id, _('cmd_start'))
        if check(message.from_user.id):
            libs.menu.show_reply_keyboard(message, bot)

    @bot.message_handler(commands=['link'])
    def link(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.from_user.id, 'https://github.com/ivanvit100')

    @bot.message_handler(commands=['help'])
    def help(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')

        help_text = f'*{_("cmd_help_title")}*\n\n{_("public_commands")}\n'
        help_text += f'{_("cmd_help")}\n{_("cmd_call")}\n{_("cmd_link")}\n{_("cmd_language")}\n'
        help_text += f'{_("cmd_menu")}\n'
        
        if config.MODULES["files"]:
            help_text += f'{_("cmd_pfiles")}\n{_("cmd_pdownload")}\n'
            
        help_text += f'\n{_("private_commands")}\n'
        
        if config.MODULES["balance"]:
            help_text += f'{_("cmd_report")}\n{_("cmd_balance")}\n{_("cmd_balance_change")}\n'
            
        if config.MODULES["notification"]:
            help_text += f'{_("cmd_notification_add")}\n{_("cmd_notification_list")}\n{_("cmd_notification_delete")}\n'
            
        if config.MODULES["task"]:
            help_text += f'{_("cmd_task_add")}\n{_("cmd_task_list")}\n{_("cmd_task_delete")}\n'
            
        if config.MODULES["email"]:
            help_text += f'{_("cmd_email_send")}\n{_("cmd_email_list")}\n'
            
        if config.MODULES["files"]:
            help_text += f'{_("cmd_save")}\n{_("cmd_share")}\n{_("cmd_download")}\n{_("cmd_delete")}\n{_("cmd_pdelete")}\n'
            
        help_text += f'{_("cmd_log")}\n'
        
        if config.MODULES["support"]:
            help_text += f'{_("cmd_ssh")}\n'
            
        if config.MODULES["vps"]:
            help_text += f'{_("cmd_stats")}\n'
            
        help_text += f'{_("cmd_language")}'
        
        bot.send_message(message.from_user.id, help_text, parse_mode='Markdown')

    @bot.message_handler(commands=['language'])
    def change_language(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("Русский", callback_data="lang_ru"),
            telebot.types.InlineKeyboardButton("English", callback_data="lang_en")
        )
        
        bot.send_message(message.from_user.id, _('language_select'), reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def callback_language(call):
        lang = call.data.split('_')[1]
        config.set_language(lang)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, _('language_changed'))

    @bot.message_handler(commands=['call'])
    def call(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        message_parts = message.text.split(' ')
        if message.from_user.id != int(USER_ID) and len(message_parts) > 1:
            bot.send_message(int(USER_ID), f'Анонимное сообщение: \n\n{message.text[6:]}')
            bot.send_message(message.from_user.id, _('message_sent'))

    @bot.message_handler(commands=['log'])
    def log(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        if not check(message.from_user.id):
            return
        
        get_log(message, bot)

    if config.MODULES["balance"]:
        from libs.balance import balance_main, report

        @bot.message_handler(commands=['balance'])
        def balance(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            balance_main(message, bot)

        @bot.message_handler(commands=['report'])
        def rpt(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            report(bot, USER_ID)

    if config.MODULES["support"]:
        from libs.support import ssh
        
        @bot.message_handler(commands=['ssh'])
        def ssh_callback(message: telebot.types.Message):
            if not check(message.from_user.id):
                return
            ssh(message, bot)

    if config.MODULES["email"]:
        from libs.email import email_main, email_read

        @bot.message_handler(commands=['email'])
        def email_command(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            email_main(message, bot)

        @bot.message_handler(func=lambda message: message.text.startswith('/email_read_'))
        def email_read_command(message: telebot.types.Message):
            if not check(message.from_user.id):
                return
            bot.send_chat_action(message.chat.id, 'typing')
            
            email_read(message, bot)

        @bot.message_handler(
            func=lambda message: message.from_user.id in libs.email.email_states 
            and libs.email.email_states[message.from_user.id]['state'] == libs.email.EmailStates.WAITING_FOR_ATTACHMENTS, 
            content_types=['document']
        )
        def email_attachment_handler(message):
            if not check(message.from_user.id):
                return
            libs.email.handle_email_attachments(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in libs.email.email_states and libs.email.email_states[message.from_user.id]['state'] == libs.email.EmailStates.WAITING_FOR_RECIPIENT)
        def email_recipient_handler(message):
            if not check(message.from_user.id):
                return
            libs.email.handle_email_recipient(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in libs.email.email_states and libs.email.email_states[message.from_user.id]['state'] == libs.email.EmailStates.WAITING_FOR_SUBJECT)
        def email_subject_handler(message):
            if not check(message.from_user.id):
                return
            libs.email.handle_email_subject(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in libs.email.email_states and libs.email.email_states[message.from_user.id]['state'] == libs.email.EmailStates.WAITING_FOR_BODY)
        def email_body_handler(message):
            if not check(message.from_user.id):
                return
            libs.email.handle_email_body(message, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data in ["email_confirm_send", "email_cancel", "email_attach_files", "email_attach_more"])
        def email_actions_callback(call):
            if not check(call.from_user.id):
                return
            if call.data == "email_confirm_send":
                libs.email.handle_email_confirm_send(call, bot)
            elif call.data == "email_cancel":
                libs.email.handle_email_cancel(call, bot)
            elif call.data in ["email_attach_files", "email_attach_more"]:
                libs.email.handle_email_attach_files(call, bot)

    if config.MODULES["files"]:
        from libs.files import save_doc, download_file, show_files, share_file, delete_file

        @bot.message_handler(content_types=['document'])
        def save_file(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            try:
                if config.MODULES["email"] and 'email' in message.caption.lower():
                    email_main(message, bot, 1)
                else:
                    save_doc(message, bot)
            except:
                save_doc(message, bot)

        @bot.message_handler(commands=["download"])
        def download(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            download_file(message, bot, 1)

        @bot.message_handler(commands=["files"])
        def list_file(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            show_files(message, bot, 1)

        @bot.message_handler(commands=["pdownload"])
        def download(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            
            download_file(message, bot)

        @bot.message_handler(commands=["pfiles"])
        def list_file(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            
            show_files(message, bot)

        @bot.message_handler(commands=["share"])
        def share(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            share_file(message, bot)

        @bot.message_handler(commands=["delete"])
        def delete(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            delete_file(message, bot, 1)

        @bot.message_handler(commands=["pdelete"])
        def delete(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            delete_file(message, bot)

    if config.MODULES["vps"]:
        from libs.vps import get_vps_data

        @bot.message_handler(commands=["stats"])
        def stats(message: telebot.types.Message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.from_user.id):
                return
            
            get_vps_data(message, bot)

    if config.MODULES["notification"]:
        from libs.notification import schedule_message, cancel_scheduled_message, schedule_list, start_notification_add, handle_notification_message

        @bot.message_handler(commands=['notification'])
        def handle_schedule(message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.chat.id):
                return
            
            message_parts = message.text.split(' ')
            
            try:
                if len(message_parts) < 3:
                    schedule_list(bot)
            
                elif message_parts[1] == 'delete':
                    job_id = int(message_parts[2])
                    cancel_scheduled_message(job_id)
                    bot.reply_to(message, f'{_("notification_deleted")} {job_id}.')
            
                else:
                    _, date, run_at, msg = message.text.split(' ', 3)
                    run_at = f"{date} {run_at}"
                    schedule_message(msg, run_at, bot)
                    logging.info(f'Notification scheduled: {run_at} {msg}')
                    bot.reply_to(message, f'{_("notification_scheduled")} {run_at}.')
            
            except Exception as e:
                logging.error(f'Error in handle_schedule: {e}')
                bot.reply_to(message, _('error_occurred'))

        @bot.message_handler(commands=['notification_add'])
        def notification_add_command(message):
            if not check(message.from_user.id):
                return
            bot.send_chat_action(message.chat.id, 'typing')
            start_notification_add(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['state'] == NotificationStates.WAITING_FOR_MESSAGE)
        def notification_text_handler(message):
            if not check(message.from_user.id):
                return
            handle_notification_message(message, bot)

    if config.MODULES["task"]:
        from libs.task import task_add, task_done, tasks_list, handle_task_title, handle_task_description, TaskStates, task_states

        @bot.message_handler(commands=['task'])
        def handle_task(message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.chat.id):
                return
            
            message_parts = message.text.split(' ')
            
            try:
                if len(message_parts) < 2:
                    tasks_list(message, bot)
                elif message_parts[1] == 'delete':
                    task_done(message, bot)
                else:
                    task_add(message, bot)
            
            except Exception as e:
                logging.error(f'Error in handle_task: {e}')
                bot.reply_to(message, _('error_occurred'))

        @bot.message_handler(func=lambda message: message.text.startswith('/task_done_'))
        def handle_task_done(message):
            bot.send_chat_action(message.chat.id, 'typing')
            if not check(message.chat.id):
                return
            
            task_done(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in task_states and task_states[message.from_user.id]['state'] == TaskStates.WAITING_FOR_TITLE)
        def task_title_handler(message):
            if not check(message.from_user.id):
                return
            handle_task_title(message, bot)

        @bot.message_handler(func=lambda message: message.from_user.id in task_states and task_states[message.from_user.id]['state'] == TaskStates.WAITING_FOR_DESCRIPTION)
        def task_description_handler(message):
            if not check(message.from_user.id):
                return
            handle_task_description(message, bot)

    @bot.message_handler(commands=['menu'])
    def menu_command(message: telebot.types.Message):
        bot.send_chat_action(message.chat.id, 'typing')
        if not check(message.from_user.id):
            return
        libs.menu.menu(message, bot)    