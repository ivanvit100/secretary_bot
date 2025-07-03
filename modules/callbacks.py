import config
from i18n import _
from libs.notification import user_states

#########################
#                       #
#       CALLBACKS       #
#                       #
#########################

def register_callbacks(bot, check_function):
    
    def check(user_id):
        return check_function(user_id)

    if config.MODULES["email"]:
        from libs.email import (
            email_read, 
            handle_email_confirm_send,
            handle_email_cancel,
            handle_email_attach_files
        )
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('email_read_'))
        def email_read_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            
            email_read(call, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data == "email_confirm_send")
        def email_confirm_send_callback(call):
            if not check(call.from_user.id):
                return
            handle_email_confirm_send(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == "email_cancel")
        def email_cancel_callback(call):
            if not check(call.from_user.id):
                return
            handle_email_cancel(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == "email_attach_files" or call.data == "email_attach_more")
        def email_attach_files_callback(call):
            if not check(call.from_user.id):
                return
            handle_email_attach_files(call, bot)

    if config.MODULES["files"]:  
        from libs.files import (
            show_files, 
            download_file, 
            delete_file_by_callback, 
            delete_files_menu, 
            share_file_by_callback, 
            share_files_menu,
        )

        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_page_'))
        def file_page_callback(call):
            parts = call.data.split('_')
            type_flag = int(parts[2])
            
            if type_flag == 1 and not check(call.from_user.id):
                return
            
            show_files(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_download_'))
        def file_download_callback(call):
            parts = call.data.split('_')
            type_flag = int(parts[2])
            
            if type_flag == 1 and not check(call.from_user.id):
                return
            
            download_file(call, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_delete_'))
        def file_delete_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            delete_file_by_callback(call, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_deletepage_'))
        def file_delete_page_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            delete_files_menu(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_share_'))
        def file_share_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            share_file_by_callback(call, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('file_sharepage_'))
        def file_share_page_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            share_files_menu(call, bot)

    if config.MODULES["task"]:
        from libs.task import (
            task_view, 
            task_done_callback, 
            task_delete_callback, 
            task_list_callback, 
            task_page_callback, 
            start_task_add, 
            handle_task_add_confirm, 
            handle_task_add_cancel
        )

        @bot.callback_query_handler(func=lambda call: call.data.startswith('task_view_'))
        def task_view_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            task_view(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('task_done_'))
        def task_complete_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            task_done_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('task_delete_'))
        def task_remove_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            task_delete_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'task_list')
        def task_list_callback_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            task_list_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('task_page_'))
        def task_page_callback_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            task_page_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'task_add')
        def task_add_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            start_task_add(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'task_add_confirm')
        def task_add_confirm_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            handle_task_add_confirm(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'task_add_cancel')
        def task_add_cancel_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            handle_task_add_cancel(call, bot)

    if config.MODULES["notification"]:
        from libs.notification import (
            notification_view, 
            notification_cancel, 
            notification_list_callback, 
            handle_calendar_callback, 
            handle_time_callback, 
            handle_notification_confirm, 
            notification_page_callback, 
            show_repeat_options, 
            set_notification_repeat
        )

        @bot.callback_query_handler(func=lambda call: call.data.startswith('notification_view_'))
        def notification_view_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            notification_view(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('notification_cancel_'))
        def notification_cancel_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            notification_cancel(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'notification_list')
        def notification_list_callback_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            notification_list_callback(call, bot)    

        @bot.callback_query_handler(func=lambda call: call.data.startswith('calendar_'))
        def calendar_callback(call):
            if not check(call.from_user.id):
                return
            handle_calendar_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('time_') or call.data.startswith('notification_back_to_'))
        def time_callback(call):
            if not check(call.from_user.id):
                return
            handle_time_callback(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data == 'notification_cancel')
        def notification_cancel_create_callback(call):
            if not check(call.from_user.id):
                return
            
            if call.from_user.id in user_states:
                del user_states[call.from_user.id]
                
            bot.edit_message_text(_('notification_cancelled_message'), call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id)

        @bot.callback_query_handler(func=lambda call: call.data == 'notification_confirm')
        def notification_confirm_callback(call):
            if not check(call.from_user.id):
                return
            handle_notification_confirm(call, bot)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('notification_page_'))
        def notification_page_callback_handler(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            notification_page_callback(call, bot)
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('notification_repeat_'))
        def notification_repeat_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            show_repeat_options(call, bot, int(call.data.split('_')[2]))
        
        @bot.callback_query_handler(func=lambda call: call.data.startswith('notification_set_repeat_'))
        def set_notification_repeat_callback(call):
            if not check(call.from_user.id):
                return
            bot.send_chat_action(call.message.chat.id, 'typing')
            set_notification_repeat(call, bot)

    from libs.menu import handle_menu_callback

    @bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
    def menu_callback_handler(call):
        if not check(call.from_user.id):
            return
        bot.send_chat_action(call.message.chat.id, 'typing')
        handle_menu_callback(call, bot)