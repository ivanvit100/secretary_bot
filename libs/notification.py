import datetime
import telebot
import logging
import os
import math
from dotenv import load_dotenv
from threading import Timer
from telebot import types
import i18n
from i18n import _

load_dotenv()

scheduled_jobs = []
USER_ID = os.getenv('USER_ID')
user_states = {}

class NotificationStates:
    IDLE = 0
    WAITING_FOR_DATE = 1
    WAITING_FOR_TIME = 2
    WAITING_FOR_MESSAGE = 3
    CONFIRMATION = 4

class NotificationData:
    def __init__(self):
        self.date = None
        self.time = None
        self.message = None
        self.orig_message_id = None

def send_delayed_message(message: str, bot: telebot.TeleBot):
    bot.send_message(USER_ID, f'*{i18n._("notification_alert")}*\n\n{message}', parse_mode="Markdown")

def schedule_message(message: str, run_at: str, bot: telebot.TeleBot):
    run_at_datetime = datetime.datetime.strptime(run_at, '%d.%m.%Y %H:%M')
    delay = (run_at_datetime - datetime.datetime.now() - datetime.timedelta(hours=3)).total_seconds()
    
    if delay > 0:
        timer = Timer(delay, send_delayed_message, [message, bot])
        scheduled_jobs.append((run_at, message, timer))
        timer.start()
        logging.info(i18n._("notification_scheduled", time=run_at))
        return True
    else:
        logging.warning(i18n._("notification_past_error", time=run_at))
        return False

def cancel_scheduled_message(index: int):
    if 0 <= index < len(scheduled_jobs):
        scheduled_jobs[index][2].cancel()
        del scheduled_jobs[index]
        logging.info(i18n._("notification_cancelled", index=index))
        return True
    else:
        logging.warning(i18n._("notification_invalid_index", index=index))
        return False

def schedule_list(bot: telebot.TeleBot, page: int = 0):
    if scheduled_jobs:
        notifications_per_page = 8
        total_pages = max(1, math.ceil(len(scheduled_jobs) / notifications_per_page))
        
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
        
        start_idx = page * notifications_per_page
        end_idx = min(start_idx + notifications_per_page, len(scheduled_jobs))
        current_page_notifications = scheduled_jobs[start_idx:end_idx]
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, job in enumerate(current_page_notifications):
            absolute_idx = start_idx + idx
            run_at, message_text = job[0], job[1]
            display_text = message_text[:30] + "..." if len(message_text) > 30 else message_text
            button_text = f"🔔 {run_at} - {display_text}"
            
            markup.add(types.InlineKeyboardButton(
                button_text, 
                callback_data=f"notification_view_{absolute_idx}"
            ))
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton(
                i18n._('prev_page'), 
                callback_data=f"notification_page_{page-1}"
            ))
        
        if page < total_pages - 1:
            nav_buttons.append(types.InlineKeyboardButton(
                i18n._('next_page'),
                callback_data=f"notification_page_{page+1}"
            ))
        
        if nav_buttons:
            markup.row(*nav_buttons)
        
        message_text = f"*{i18n._('notification_list_title')}*"
        if total_pages > 1:
            message_text += f"\n_{i18n._('page')} {page + 1} {i18n._('of')} {total_pages}_"
        
        bot.send_message(
            USER_ID,
            message_text, 
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.send_message(USER_ID, i18n._("notification_list_empty"))

def notification_view(call, bot: telebot.TeleBot):
    try:
        notification_index = int(call.data.split('_')[2])
        
        if 0 <= notification_index < len(scheduled_jobs):
            run_at, message_text, timer = scheduled_jobs[notification_index]
            
            run_at_datetime = datetime.datetime.strptime(run_at, '%d.%m.%Y %H:%M')
            time_remaining = run_at_datetime - datetime.datetime.now()
            days, seconds = time_remaining.days, time_remaining.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            time_remaining_str = f"{days}д {hours}ч {minutes}м" if days > 0 else f"{hours}ч {minutes}м"
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton(
                    i18n._('notification_button_cancel'), 
                    callback_data=f"notification_cancel_{notification_index}"
                ),
                types.InlineKeyboardButton(
                    i18n._('notification_button_back'), 
                    callback_data="notification_list"
                )
            )
            
            notification_text = (
                f"*{i18n._('notification_details')}*\n\n"
                f"{i18n._('notification_date')}: `{run_at}`\n"
                f"{i18n._('notification_time_remaining')}: `{time_remaining_str}`\n\n"
                f"{i18n._('notification_message')}:\n{message_text}"
            )
            
            bot.edit_message_text(
                notification_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        else:
            bot.answer_callback_query(call.id, i18n._('notification_not_found'))
            
    except Exception as e:
        logging.error(f"Error in notification_view: {e}")
        bot.answer_callback_query(call.id, i18n._('notification_error'))

def notification_cancel(call, bot: telebot.TeleBot):
    try:
        notification_index = int(call.data.split('_')[2])
        
        if 0 <= notification_index < len(scheduled_jobs):
            run_at = scheduled_jobs[notification_index][0]
            
            cancel_scheduled_message(notification_index)
            
            if scheduled_jobs:
                notification_list_callback(call, bot, 0)
                bot.answer_callback_query(call.id, i18n._('notification_cancelled_short'))
            else:
                bot.edit_message_text(
                    i18n._('notification_list_empty'),
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )
                bot.answer_callback_query(call.id, i18n._('notification_cancelled_short'))
        else:
            bot.answer_callback_query(call.id, i18n._('notification_not_found'))
            
    except Exception as e:
        logging.error(f"Error in notification_cancel: {e}")
        bot.answer_callback_query(call.id, i18n._('notification_error'))

def notification_list_callback(call, bot: telebot.TeleBot, page: int = 0):
    try:
        bot.answer_callback_query(call.id)
        
        if scheduled_jobs:
            notifications_per_page = 8
            total_pages = max(1, math.ceil(len(scheduled_jobs) / notifications_per_page))
            
            if page < 0:
                page = 0
            elif page >= total_pages:
                page = total_pages - 1
            
            start_idx = page * notifications_per_page
            end_idx = min(start_idx + notifications_per_page, len(scheduled_jobs))
            current_page_notifications = scheduled_jobs[start_idx:end_idx]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for idx, job in enumerate(current_page_notifications):
                absolute_idx = start_idx + idx
                run_at, message_text = job[0], job[1]
                display_text = message_text[:30] + "..." if len(message_text) > 30 else message_text
                button_text = f"🔔 {run_at} - {display_text}"
                
                markup.add(types.InlineKeyboardButton(
                    button_text, 
                    callback_data=f"notification_view_{absolute_idx}"
                ))
            
            nav_buttons = []
            if page > 0:
                nav_buttons.append(types.InlineKeyboardButton(
                    i18n._('prev_page'), 
                    callback_data=f"notification_page_{page-1}"
                ))
            
            if page < total_pages - 1:
                nav_buttons.append(types.InlineKeyboardButton(
                    i18n._('next_page'),
                    callback_data=f"notification_page_{page+1}"
                ))
            
            if nav_buttons:
                markup.row(*nav_buttons)
            
            message_text = f"*{i18n._('notification_list_title')}*"
            if total_pages > 1:
                message_text += f"\n_{i18n._('page')} {page + 1} {i18n._('of')} {total_pages}_"
            
            bot.edit_message_text(
                message_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.edit_message_text(
                i18n._('notification_list_empty'),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logging.error(f"Error in notification_list_callback: {e}")
        bot.answer_callback_query(call.id, i18n._('notification_error'))

def notification_page_callback(call, bot: telebot.TeleBot):
    try:
        page = int(call.data.split('_')[2])
        notification_list_callback(call, bot, page)
    except Exception as e:
        logging.error(f"Error in notification_page_callback: {e}")
        bot.answer_callback_query(call.id, i18n._('notification_error'))

def start_notification_add(message: telebot.types.Message, bot: telebot.TeleBot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_states[user_id] = {
        'state': NotificationStates.WAITING_FOR_DATE,
        'data': NotificationData()
    }
    user_states[user_id]['data'].orig_message_id = message.message_id
    
    now = datetime.datetime.now()
    calendar_markup = create_calendar(now.year, now.month)
    
    sent_msg = bot.send_message(
        chat_id,
        i18n._('notification_select_date'),
        reply_markup=calendar_markup,
        parse_mode='Markdown'
    )
    
    user_states[user_id]['message_id'] = sent_msg.message_id

def create_calendar(year, month):
    markup = types.InlineKeyboardMarkup(row_width=7)
    
    markup.add(
        types.InlineKeyboardButton(
            f"{get_month_name(month)} {year}",
            callback_data="calendar_ignore"
        )
    )
    
    week_days = [i18n._('mon'), i18n._('tue'), i18n._('wed'), i18n._('thu'), i18n._('fri'), i18n._('sat'), i18n._('sun')]
    week_row = [types.InlineKeyboardButton(day, callback_data="calendar_ignore") for day in week_days]
    markup.row(*week_row)
    
    month_calendar = datetime.datetime(year, month, 1).replace(day=1)
    first_day_of_week = month_calendar.weekday()
    last_day = (datetime.datetime(year, month + 1, 1) - datetime.timedelta(days=1)).day if month < 12 else (datetime.datetime(year + 1, 1, 1) - datetime.timedelta(days=1)).day
    
    day = 1
    row = []
    
    for _ in range(first_day_of_week):
        row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
    
    while day <= last_day:
        is_today = day == datetime.datetime.now().day and month == datetime.datetime.now().month and year == datetime.datetime.now().year
        is_future = datetime.datetime(year, month, day) > datetime.datetime.now()
        
        if is_today or is_future:
            row.append(types.InlineKeyboardButton(
                str(day), 
                callback_data=f"calendar_day_{year}_{month}_{day}"
            ))
        else:
            row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
        
        if len(row) == 7 or day == last_day:
            markup.row(*row)
            row = []
        
        day += 1
    
    nav_row = []
    
    if year > datetime.datetime.now().year or (year == datetime.datetime.now().year and month > datetime.datetime.now().month):
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        nav_row.append(types.InlineKeyboardButton(
            "◀️", 
            callback_data=f"calendar_month_{prev_year}_{prev_month}"
        ))
    else:
        nav_row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
    
    nav_row.append(types.InlineKeyboardButton(
        i18n._('notification_cancel'), 
        callback_data="notification_cancel"
    ))
    
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    if next_year <= datetime.datetime.now().year + 1:
        nav_row.append(types.InlineKeyboardButton(
            "▶️", 
            callback_data=f"calendar_month_{next_year}_{next_month}"
        ))
    else:
        nav_row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
    
    markup.row(*nav_row)
    
    return markup

def get_month_name(month_num):
    months = [
        i18n._('january'), i18n._('february'), i18n._('march'), 
        i18n._('april'), i18n._('may'), i18n._('june'), 
        i18n._('july'), i18n._('august'), i18n._('september'), 
        i18n._('october'), i18n._('november'), i18n._('december')
    ]
    return months[month_num - 1]

def create_time_picker():
    markup = types.InlineKeyboardMarkup(row_width=4)
    
    markup.add(types.InlineKeyboardButton(i18n._('notification_select_hour'), callback_data="time_ignore"))
    
    hours = []
    for hour in range(24):
        hours.append(types.InlineKeyboardButton(
            f"{hour:02d}", 
            callback_data=f"time_hour_{hour}"
        ))
        
        if len(hours) == 4:
            markup.row(*hours)
            hours = []
    
    markup.add(types.InlineKeyboardButton(
        i18n._('notification_back'), 
        callback_data="notification_back_to_date"
    ))
    
    return markup

def create_minute_picker(hour):
    markup = types.InlineKeyboardMarkup(row_width=4)
    
    markup.add(types.InlineKeyboardButton(
        i18n._('notification_select_minute', hour=f"{hour:02d}"), 
        callback_data="time_ignore"
    ))
    
    minutes = []
    for minute in range(0, 60, 5):
        minutes.append(types.InlineKeyboardButton(
            f"{minute:02d}", 
            callback_data=f"time_minute_{hour}_{minute}"
        ))
        
        if len(minutes) == 4:
            markup.row(*minutes)
            minutes = []
    
    if minutes:
        markup.row(*minutes)
    
    markup.add(types.InlineKeyboardButton(
        i18n._('notification_back'), 
        callback_data="notification_back_to_hour"
    ))
    
    return markup

def handle_calendar_callback(call, bot: telebot.TeleBot):
    user_id = call.from_user.id
    
    if call.data == "notification_cancel":
        del user_states[user_id]
        bot.edit_message_text(
            i18n._('notification_cancelled_message'),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("calendar_day_"):
        _, _, year, month, day = call.data.split('_')
        year, month, day = int(year), int(month), int(day)
        
        selected_date = datetime.date(year, month, day)
        if selected_date < datetime.date.today():
            bot.answer_callback_query(call.id, i18n._('notification_past_date_error'))
            return
        
        user_states[user_id]['data'].date = f"{day:02d}.{month:02d}.{year}"
        user_states[user_id]['state'] = NotificationStates.WAITING_FOR_TIME
        
        bot.edit_message_text(
            i18n._('notification_date_selected', date=user_states[user_id]['data'].date) + "\n" + i18n._('notification_select_time'),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_time_picker()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("calendar_month_"):
        _, _, year, month = call.data.split('_')
        year, month = int(year), int(month)
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_calendar(year, month)
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "calendar_ignore":
        bot.answer_callback_query(call.id)
        return

def handle_time_callback(call, bot: telebot.TeleBot):
    user_id = call.from_user.id
    
    if call.data == "notification_back_to_date":
        user_states[user_id]['state'] = NotificationStates.WAITING_FOR_DATE
        
        now = datetime.datetime.now()
        bot.edit_message_text(
            i18n._('notification_select_date'),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_calendar(now.year, now.month)
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "notification_back_to_hour":
        bot.edit_message_text(
            i18n._('notification_date_selected', date=user_states[user_id]['data'].date) + "\n" + i18n._('notification_select_time'),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_time_picker()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("time_hour_"):
        hour = int(call.data.split('_')[2])
        bot.edit_message_text(
            i18n._('notification_date_selected', date=user_states[user_id]['data'].date) + "\n" + i18n._('notification_hour_selected', hour=f"{hour:02d}"),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_minute_picker(hour)
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("time_minute_"):
        _, _, hour, minute = call.data.split('_')
        hour, minute = int(hour), int(minute)
        
        user_states[user_id]['data'].time = f"{hour:02d}:{minute:02d}"
        user_states[user_id]['state'] = NotificationStates.WAITING_FOR_MESSAGE
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            i18n._('notification_cancel'), 
            callback_data="notification_cancel"
        ))
        
        bot.edit_message_text(
            i18n._('notification_datetime_selected', date=user_states[user_id]['data'].date, time=user_states[user_id]['data'].time) + "\n\n" + i18n._('notification_enter_message'),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "time_ignore":
        bot.answer_callback_query(call.id)
        return

def handle_notification_message(message, bot: telebot.TeleBot):
    user_id = message.from_user.id
    
    if user_id in user_states and user_states[user_id]['state'] == NotificationStates.WAITING_FOR_MESSAGE:
        user_states[user_id]['data'].message = message.text
        user_states[user_id]['state'] = NotificationStates.CONFIRMATION
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                i18n._('notification_confirm'), 
                callback_data="notification_confirm"
            ),
            types.InlineKeyboardButton(
                i18n._('notification_cancel'), 
                callback_data="notification_cancel"
            )
        )
        
        date = user_states[user_id]['data'].date
        time = user_states[user_id]['data'].time
        notification_text = user_states[user_id]['data'].message
        
        preview_text = (
            f"*{i18n._('notification_preview')}*\n\n"
            f"{i18n._('notification_date')}: `{date}`\n"
            f"{i18n._('notification_time')}: `{time}`\n\n"
            f"{i18n._('notification_text')}:\n{notification_text}\n\n"
            f"{i18n._('notification_confirm_prompt')}"
        )
        
        bot.delete_message(
            message.chat.id,
            user_states[user_id]['message_id']
        )
        
        sent_msg = bot.send_message(
            message.chat.id,
            preview_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        user_states[user_id]['message_id'] = sent_msg.message_id
        
        bot.delete_message(message.chat.id, message.message_id)

def handle_notification_confirm(call, bot: telebot.TeleBot):
    user_id = call.from_user.id
    
    if user_id in user_states and user_states[user_id]['state'] == NotificationStates.CONFIRMATION:
        date = user_states[user_id]['data'].date
        time = user_states[user_id]['data'].time
        notification_text = user_states[user_id]['data'].message
        
        run_at = f"{date} {time}"
        
        success = schedule_message(notification_text, run_at, bot)
        
        if success:
            bot.edit_message_text(
                i18n._('notification_created_success', date=date, time=time),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                i18n._('notification_creation_failed'),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
        
        del user_states[user_id]
        
        bot.answer_callback_query(call.id)