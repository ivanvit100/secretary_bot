import telebot
from telebot import types
import config
from i18n import _
import logging
from libs.email import (
    start_email_send, handle_email_confirm_send, 
    handle_email_cancel, handle_email_attach_files
)

ssh_mode_users = {}

def menu(message, bot):
    show_main_menu(message, bot)

def show_main_menu(message_or_call, bot):
    try:
        if isinstance(message_or_call, telebot.types.CallbackQuery):
            message = message_or_call.message
            bot.answer_callback_query(message_or_call.id)
        else:
            message = message_or_call
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        if config.MODULES["notification"]:
            buttons.append(types.InlineKeyboardButton(_("menu_notifications_button"), callback_data="menu_notifications"))
        
        if config.MODULES["task"]:
            buttons.append(types.InlineKeyboardButton(_("menu_tasks_button"), callback_data="menu_tasks"))
        
        if config.MODULES["email"]:
            buttons.append(types.InlineKeyboardButton(_("menu_email_button"), callback_data="menu_email"))
        
        if config.MODULES["balance"]:
            buttons.append(types.InlineKeyboardButton(_("menu_balance_button"), callback_data="menu_balance"))
            buttons.append(types.InlineKeyboardButton(_("menu_report_button"), callback_data="menu_report"))
        
        if config.MODULES["vps"]:
            buttons.append(types.InlineKeyboardButton(_("menu_vps_button"), callback_data="menu_vps"))
        
        if config.MODULES["files"]:
            buttons.append(types.InlineKeyboardButton(_("menu_files_button"), callback_data="menu_files"))
        
        buttons.append(types.InlineKeyboardButton(_("menu_log_button"), callback_data="menu_log"))
        
        if config.MODULES["support"]:
            buttons.append(types.InlineKeyboardButton(_("menu_ssh_button"), callback_data="menu_ssh"))
        
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                markup.row(buttons[i], buttons[i+1])
            else:
                markup.row(buttons[i])
        
        if isinstance(message_or_call, telebot.types.CallbackQuery):
            bot.edit_message_text(
                _("menu_main_title"), 
                message.chat.id, 
                message.message_id,
                parse_mode="Markdown", 
                reply_markup=markup
            )
        else:
            bot.send_message(
                message.chat.id, 
                _("menu_main_title"), 
                parse_mode="Markdown", 
                reply_markup=markup
            )
    except Exception as e:
        logging.error(f"Error in show_main_menu: {e}")
        if isinstance(message_or_call, telebot.types.CallbackQuery):
            bot.answer_callback_query(message_or_call.id, text=_("error_occurred"))
        else:
            bot.send_message(message_or_call.chat.id, _("error_occurred"))

def show_notifications_menu(call, bot):
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        markup.add(
            types.InlineKeyboardButton(_("menu_notification_list_button"), callback_data="menu_notification_list"),
            types.InlineKeyboardButton(_("menu_notification_add_button"), callback_data="menu_notification_add"),
            types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main")
        )
        
        bot.edit_message_text(
            _("menu_notifications_title"),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Error in show_notifications_menu: {e}")
        bot.answer_callback_query(call.id, text=_("error_occurred"))

def show_files_menu(call, bot):
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        markup.add(
            types.InlineKeyboardButton(_("menu_files_private_button"), callback_data="menu_files_private"),
            types.InlineKeyboardButton(_("menu_files_public_button"), callback_data="menu_files_public"),
            types.InlineKeyboardButton(_("menu_files_upload_button"), callback_data="menu_files_upload"),
            types.InlineKeyboardButton(_("menu_files_delete_button"), callback_data="menu_files_delete"),
            types.InlineKeyboardButton(_("menu_files_pdelete_button"), callback_data="menu_files_pdelete"),
            types.InlineKeyboardButton(_("menu_files_share_button"), callback_data="menu_files_share"),
            types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main")
        )
        
        bot.edit_message_text(
            _("menu_files_title"),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Error in show_files_menu: {e}")
        bot.answer_callback_query(call.id, text=_("error_occurred"))

def is_in_ssh_mode(user_id):
    return user_id in ssh_mode_users

def process_ssh_message(message, bot):
    user_id = message.from_user.id
    
    if user_id in ssh_mode_users:
        try:
            msg_id = ssh_mode_users.pop(user_id)
            
            bot.delete_message(message.chat.id, msg_id)
            
            if config.MODULES["support"]:
                from libs.support import ssh
                
                cmd_text = f"/ssh {message.text}"
                ssh_message = telebot.types.Message(
                    message_id=message.message_id,
                    from_user=message.from_user,
                    date=message.date,
                    chat=message.chat,
                    content_type='text',
                    options={},
                    json_string=''
                )
                ssh_message.text = cmd_text
                
                bot.delete_message(message.chat.id, message.message_id)
                ssh(ssh_message, bot)
            
            return True
        except Exception as e:
            logging.error(f"Error processing SSH message: {e}")
            bot.send_message(message.chat.id, _("menu_ssh_command_error"))
            return True
    
    return False

def handle_menu_callback(call, bot):
    try:
        callback_data = call.data
        
        if callback_data == "menu_main":
            show_main_menu(call, bot)
        
        # Уведомления
        elif callback_data == "menu_notifications":
            show_notifications_menu(call, bot)
        elif callback_data == "menu_notification_list":
            bot.answer_callback_query(call.id)
            if config.MODULES["notification"]:
                from libs.notification import schedule_list
                schedule_list(bot)
        elif callback_data == "menu_notification_add":
            bot.answer_callback_query(call.id)
            if config.MODULES["notification"]:
                from libs.notification import start_notification_add
                start_notification_add(call.message, bot)
        
        # Задачи
        elif callback_data == "menu_tasks":
            bot.answer_callback_query(call.id)
            if config.MODULES["task"]:
                try:
                    from libs.task import tasks_list
                    task_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    tasks_list(task_message, bot)
                except Exception as e:
                    logging.error(f"Error showing tasks: {e}")
                    bot.send_message(call.message.chat.id, _("menu_tasks_error").format(error=e))
        
        # Email
        elif callback_data == "menu_email":
            bot.answer_callback_query(call.id)
            if config.MODULES["email"]:
                try:
                    import os
                    email_address = os.getenv('EMAIL_ADDRESS')

                    if ',' in email_address:
                        email_list = [email.strip() for email in email_address.split(',')]
                        markup = types.InlineKeyboardMarkup(row_width=1)

                        for idx, email in enumerate(email_list):
                            markup.add(types.InlineKeyboardButton(f"📧 {email}", callback_data=f"menu_email_select_{idx}_{email}"))

                        markup.add(types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main"))

                        bot.edit_message_text(
                            _("menu_email_select_title"),
                            call.message.chat.id,
                            call.message.message_id,
                            parse_mode="Markdown",
                            reply_markup=markup
                        )
                    else:
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        markup.add(
                            types.InlineKeyboardButton(_("menu_email_send_button"), callback_data="menu_email_send_0"),
                            types.InlineKeyboardButton(_("menu_email_read_button"), callback_data="menu_email_list_0"),
                            types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main")
                        )

                        bot.edit_message_text(
                            _("menu_email_mailbox_title").format(email=email_address),
                            call.message.chat.id,
                            call.message.message_id,
                            parse_mode="Markdown",
                            reply_markup=markup
                        )
                except Exception as e:
                    logging.error(f"Error handling email menu: {e}")
                    bot.send_message(call.message.chat.id, _("menu_email_error").format(error=e))
        elif callback_data.startswith("menu_email_select_"):
            bot.answer_callback_query(call.id)
            parts = callback_data.replace("menu_email_select_", "").split('_', 1)
            email_idx = int(parts[0])
            selected_email = parts[1]

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(_("menu_email_send_button"), callback_data=f"menu_email_send_{email_idx}"),
                types.InlineKeyboardButton(_("menu_email_read_button"), callback_data=f"menu_email_list_{email_idx}"),
                types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_email")
            )

            bot.edit_message_text(
                _("menu_email_mailbox_title").format(email=selected_email),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        # Обрабатываем нажатие кнопки "Входящие"
        elif callback_data.startswith("menu_email_list_"):
            bot.answer_callback_query(call.id)
            if config.MODULES["email"]:
                try:
                    email_index = int(callback_data.replace("menu_email_list_", ""))

                    from libs.email import email_main

                    email_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    email_message.text = ''
                    email_main(email_message, bot, 0, email_index)
                except Exception as e:
                    logging.error(f"Error getting email list: {e}")
                    bot.send_message(call.message.chat.id, _("menu_email_read_error").format(error=e))
        # Обработчик для чтения email
        elif callback_data.startswith("email_read_"):
            bot.answer_callback_query(call.id)
            if config.MODULES["email"]:
                try:
                    parts = callback_data.split('_')

                    if len(parts) == 3:
                        email_index = int(parts[2])
                        from libs.email import email_main

                        email_message = telebot.types.Message(
                            message_id=call.message.message_id,
                            from_user=call.from_user,
                            date=call.message.date,
                            chat=call.message.chat,
                            content_type='text',
                            options={},
                            json_string=''
                        )
                        email_message.text = f'/email'
                        email_main(email_message, bot, 0, email_index)

                    elif len(parts) == 4:
                        email_index = int(parts[2])
                        message_index = int(parts[3])

                        from libs.email import email_read

                        email_message = telebot.types.Message(
                            message_id=call.message.message_id,
                            from_user=call.from_user,
                            date=call.message.date,
                            chat=call.message.chat,
                            content_type='text',
                            options={},
                            json_string=''
                        )
                        email_message.text = f'/email_read_{email_index}_{message_index}'
                        email_read(email_message, bot)
                    else:
                        message_index = int(parts[2])

                        from libs.email import email_read

                        email_message = telebot.types.Message(
                            message_id=call.message.message_id,
                            from_user=call.from_user,
                            date=call.message.date,
                            chat=call.message.chat,
                            content_type='text',
                            options={},
                            json_string=''
                        )
                        email_message.text = f'/email_read_{message_index}'
                        email_read(email_message, bot)

                except Exception as e:
                    logging.error(f"Error processing email action: {e}")
            bot.send_message(call.message.chat.id, _("menu_email_read_error").format(error=e))
        # В обработчике меню для кнопок email
        elif callback_data.startswith("menu_email_send_"):
            bot.answer_callback_query(call.id)
            if config.MODULES["email"]:
                try:
                    email_idx = int(callback_data.replace("menu_email_send_", ""))
                    from libs.email import start_email_send
                    start_email_send(call, bot, email_idx)
                except Exception as e:
                    logging.error(f"Error starting email send: {e}")
                    bot.send_message(call.message.chat.id, _("menu_email_send_error").format(error=e))
        # Обработчики кнопок для подтверждения email
        elif callback_data == "email_confirm_send":
            from libs.email import handle_email_confirm_send
            handle_email_confirm_send(call, bot)
        elif callback_data == "email_cancel":
            from libs.email import handle_email_cancel
            handle_email_cancel(call, bot)
        elif callback_data == "email_attach_files":
            from libs.email import handle_email_attach_files
            handle_email_attach_files(call, bot)
        
        # Баланс
        elif callback_data == "menu_balance":
            bot.answer_callback_query(call.id)
            if config.MODULES["balance"]:
                try:
                    from libs.balance import balance_main
                    balance_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    balance_message.text = '/balance'
                    balance_main(balance_message, bot)
                except Exception as e:
                    logging.error(f"Error handling balance: {e}")
                    bot.send_message(call.message.chat.id, _("menu_balance_error").format(error=e))
        
        # Отчет
        elif callback_data == "menu_report":
            bot.answer_callback_query(call.id)
            if config.MODULES["balance"]:
                from libs.balance import report
                report(bot, call.message.chat.id)
        
        # VPS
        elif callback_data == "menu_vps":
            bot.answer_callback_query(call.id)
            if config.MODULES["vps"]:
                try:
                    from libs.vps import get_vps_data
                    vps_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    vps_message.text = '/stats'
                    get_vps_data(vps_message, bot)
                except Exception as e:
                    logging.error(f"Error handling VPS stats: {e}")
                    bot.send_message(call.message.chat.id, _("menu_vps_error").format(error=e))
        
        # Файлы
        elif callback_data == "menu_files":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton(_("menu_files_private"), callback_data="menu_files_private"),
                    types.InlineKeyboardButton(_("menu_files_public"), callback_data="menu_files_public"),
                    types.InlineKeyboardButton(_("menu_files_delete"), callback_data="menu_files_delete"),
                    types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_main")
                )

                bot.edit_message_text(
                    _("menu_files_title"),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        elif callback_data == "menu_files_delete":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton(_("menu_files_delete_private"), callback_data="menu_files_delete_private"),
                    types.InlineKeyboardButton(_("menu_files_delete_public"), callback_data="menu_files_delete_public"),
                    types.InlineKeyboardButton(_("menu_back_button"), callback_data="menu_files")
                )

                bot.edit_message_text(
                    _("menu_files_delete_title"),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        # Обработчики для команд удаления приватных и публичных файлов
        elif callback_data == "menu_files_delete_private":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                from libs.files import delete_files_menu
                delete_files_menu(call, bot, 1)
        elif callback_data == "menu_files_delete_public":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                from libs.files import delete_files_menu
                delete_files_menu(call, bot, 0)
        elif callback_data == "menu_files_private":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                try:
                    from libs.files import show_files
                    file_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    show_files(file_message, bot, 1)
                except Exception as e:
                    logging.error(f"Error showing private files: {e}")
                    bot.send_message(call.message.chat.id, _("menu_files_error").format(error=e))
        elif callback_data == "menu_files_public":
            bot.answer_callback_query(call.id)
            if config.MODULES["files"]:
                try:
                    from libs.files import show_files
                    file_message = telebot.types.Message(
                        message_id=call.message.message_id,
                        from_user=call.from_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=''
                    )
                    show_files(file_message, bot, 0)
                except Exception as e:
                    logging.error(f"Error showing public files: {e}")
                    bot.send_message(call.message.chat.id, _("menu_files_error").format(error=e))

        # Лог
        elif callback_data == "menu_log":
            bot.answer_callback_query(call.id)
            try:
                from libs.support import get_log
                log_message = telebot.types.Message(
                    message_id=call.message.message_id,
                    from_user=call.from_user,
                    date=call.message.date,
                    chat=call.message.chat,
                    content_type='text',
                    options={},
                    json_string=''
                )
                log_message.text = '/log'
                get_log(log_message, bot)
            except Exception as e:
                logging.error(f"Error handling log: {e}")
                bot.send_message(call.message.chat.id, _("menu_log_error").format(error=e))
        
        # SSH
        elif callback_data == "menu_ssh":
            bot.answer_callback_query(call.id)
            msg = bot.send_message(call.message.chat.id, _("menu_ssh_enter_command"))
            ssh_mode_users[call.from_user.id] = msg.message_id
        
    except Exception as e:
        logging.error(f"Error in handle_menu_callback: {e}")
        bot.answer_callback_query(call.id, text=_("error_occurred"))