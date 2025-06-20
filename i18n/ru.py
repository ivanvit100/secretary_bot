messages = {
    # Описание команд
    "cmd_start": "Приветствую! Я бот - личный секретарь.\nСвоего босса не раскрою, но если хотите себе такого же, введите /link.\nЕсли хотите узнать, что я умею, введите /help.\nЧтобы написать моему боссу анонимное сообщение, введите /call.",
    "cmd_help_title": "Список команд",
    
    # Общедоступные комманды
    "public_commands": "Общедоступные команды:",
    "cmd_help": "- /help - список команд",
    "cmd_call": "- /call - написать владельцу бота",
    "cmd_pfiles": "- /pfiles - посмотреть список общедоступных файлов",
    "cmd_pdownload": "- /pdownload <название> - скачать общедоступный файл",
    "cmd_link": "- /link - ссылка на исходный код бота",
    "cmd_language": "- /language - изменить язык бота",
    
    # Приватные комманды
    "private_commands": "Приватные команды:",
    "cmd_report": "- /report - отчёт по балансу",
    "cmd_balance": "- /balance - текущий баланс",
    "cmd_balance_change": "- /balance <число> - изменить баланс на число",
    "cmd_notification_add": "- /notification_add - добавить уведомление",
    "cmd_notification_list": "- /notification - список уведомлений",
    "cmd_notification_delete": "- /notification delete <номер> - удалить уведомление",
    "cmd_task_add": "- /task <сообщение> - добавить задачу",
    "cmd_task_list": "- /task - список задач",
    "cmd_task_delete": "- /task delete <номер> - удалить задачу",
    "cmd_email_send": "- /email <address> <сообщение> - отправить сообщение на почту",
    "cmd_email_list": "- /email - список сообщений на почту",
    "cmd_save": "- /save - сохранить файл на веб-сервере",
    "cmd_share": "- /share <название> - поделиться файлом",
    "cmd_download": "- /download <название> - скачать файл",
    "cmd_delete": "- /delete <название> - удалить файл",
    "cmd_pdelete": "- /pdelete <название> - удалить общедоступный файл",
    "cmd_log": "- /log - лог действий",
    "cmd_ssh": "- /ssh <команда> - выполнить команду на сервере",
    "cmd_stats": "- /stats - статистика Beget",
    
    # Общие сообщения
    "no_permission": "У вас нет прав для выполнения этой команды",
    "error_occurred": "Произошла ошибка",
    "message_sent": "Сообщение отправлено",
    
    # Ежедневный отчёт
    "daily_summary_title": "Краткая сводка на день",
    "daily_balance": "Баланс",
    "daily_saldo": "Сальдо",
    "daily_tasks": "Задачи",
    "daily_completed": "Выполнено в этом месяце",
    
    # Запуск
    "secretary_started": "Секретарь запущен",
    
    # Язык
    "language_changed": "Язык изменен на русский",
    "language_select": "Выберите язык:",

    # Основные сообщения баланса
    "balance_current_month": "Текущий месяц: {month}\n\nВаш баланс: `{balance}`\nСальдо: `{saldo}`",
    "balance_updated": "Баланс обновлен: `{value}`",
    "balance_invalid_format": "Неверный формат параметра",
    
    # Отчет по балансу
    "balance_report_title": "Отчёт по балансу",
    "balance_forecast_current": "Прогнозированный баланс на текущий месяц: `{value}`",
    "balance_forecast_saldo_current": "Прогнозированное сальдо на текущий месяц: `{value}`",
    "balance_forecast_next": "Прогнозированный баланс на следующий месяц: `{value}`",
    "balance_forecast_saldo_next": "Прогнозированное сальдо на следующий месяц: `{value}`",
    "balance_current_income": "Текущие доходы: `{value}`",
    "balance_current_expenses": "Текущие расходы: `{value}`",
    "balance_avg_year": "Средний баланс за год: `{value}`",
    "balance_avg_saldo_year": "Среднее сальдо за год: `{value}`",
    "balance_max_year": "Максимальный баланс за год: `{value}` ({month})",
    "balance_min_year": "Минимальный баланс за год: `{value}` ({month})",
    "balance_total_year": "Итоговый приход за год: `{value}`",
    "balance_report_error": "Произошла ошибка при отправке отчёта.",
    
    # Сброс баланса
    "balance_reset_title": "Ежемесячный сброс баланса",
    "balance_reset_message": "Баланс на начало месяца: {value} (перенесено с {month})",
    "balance_reset_saldo": "Сальдо обнулено",
    "balance_reset_daily": "Доходы и расходы по дням сброшены",
    "balance_reset_month_not_found": "Ошибка: месяц {month} не найден в файле баланса",
    "balance_reset_error": "Произошла ошибка при сбросе баланса: {error}",

    # Email сообщения
    "email_no_messages": "Нет новых сообщений",
    "email_list_title": "Список последних сообщений для `{email}`:",
    "email_sent_success": "Сообщение успешно отправлено на почту ✅",
    "email_error": "Произошла ошибка при отправке сообщения",
    "email_subject_default": "Сообщение от {name}",
    "email_read_error": "Произошла ошибка при обработке сообщения",
    "email_send_failed": "Не удалось отправить email",
    "email_no_subject": "Без темы",

    # Файловые операции
    "file_saved": "Файл сохранен",
    "file_error": "Произошла ошибка",
    "file_deleted": "Файл удален", 
    "file_shared": "Файл перемещен в общедоступные файлы",
    "file_not_found": "Файл не найден",
    "files_list_empty": "Список файлов пуст",
    "private_files_title": "Личные файлы",
    "public_files_title": "Общедоступные файлы",
    "prev_page": "Назад",
    "next_page": "Вперед",
    "page": "Страница",
    "of": "из",

    # Уведомления
    "notification_alert": "Внимание! Новое уведомление!",
    "notification_list_title": "Уведомления",
    "notification_list_empty": "У вас нет запланированных уведомлений.",
    "notification_past_error": "Невозможно запланировать уведомление в прошлом: {time}",
    "notification_cancelled": "Уведомление отменено с индексом {index}",
    "notification_invalid_index": "Не найдено уведомление с индексом {index}",
    "notification_scheduled": "Уведомление запланировано на {time}",
    "notification_button_cancel": "❌ Отменить",
    "notification_button_back": "⬅️ Назад к списку",
    "notification_details": "Детали уведомления",
    "notification_date": "Дата и время",
    "notification_time_remaining": "Осталось времени",
    "notification_message": "Сообщение",
    "notification_not_found": "Уведомление не найдено",
    "notification_error": "Произошла ошибка",
    "notification_cancelled_short": "Уведомление отменено!",
    "notification_cancelled_message": "✅ Уведомление на {time} отменено",
    "notification_datetime_selected": "📅 Выбранная дата: *{date}*\n⏰ Выбранное время: *{time}*",
    "notification_enter_message": "✏️ Теперь *отправьте сообщение* для уведомления:",
    "notification_cancel": "❌ Отменить",
    "notification_text": "Текст",
    "notification_time": "Время",
    "notification_confirm_prompt": "Подтвердите создание уведомления:",
    "notification_confirm": "✅ Создать",
    "notification_preview": "📋 Предпросмотр уведомления",
    "notification_date_selected": "📅 Выбранная дата: *{date}*",
    "notification_select_time": "⏰ *Выберите время* для уведомления:",
    "notification_back": "⬅️ Назад",
    "notification_select_hour": "Выберите час:",
    "notification_select_minute": "Выберите минуты (час: {hour}):",
    "notification_hour_selected": "⏰ Выбран час: *{hour}*",
    "notification_select_date": "📅 *Выберите дату* для уведомления:",
    "notification_past_date_error": "Невозможно выбрать прошедшую дату",
    "notification_created_success": "✅ Уведомление успешно создано на *{date}* в *{time}*",
    "notification_creation_failed": "❌ Не удалось создать уведомление. Возможно, выбрано прошедшее время.",
    "notification_back_to_date": "Вернуться к выбору даты",
    "notification_back_to_hour": "Вернуться к выбору часа",

    # Дни недели и месяцы
    "mon": "Пн", "tue": "Вт", "wed": "Ср", 
    "thu": "Чт", "fri": "Пт", "sat": "Сб", "sun": "Вс",
    "january": "Январь", "february": "Февраль", "march": "Март",
    "april": "Апрель", "may": "Май", "june": "Июнь",
    "july": "Июль", "august": "Август", "september": "Сентябрь",
    "october": "Октябрь", "november": "Ноябрь", "december": "Декабрь",

    # Графики
    "plot_balance_label": "Баланс",
    "plot_saldo_label": "Сальдо",
    "plot_month_label": "Месяц",
    "plot_amount_label": "Сумма",
    "plot_balance_title": "Баланс и сальдо по месяцам",
    "plot_income_label": "Доход",
    "plot_expenses_label": "Расходы",
    "plot_income_legend": "доходы",
    "plot_expenses_legend": "расходы",
    "plot_month_stats_title": "Статистика за месяц",
    "plot_balance_saved": "График баланса сохранен как balance_plot.png",
    "plot_income_saved": "График доходов и расходов сохранен как income_expenses_plot.png",
    "plot_zero_income_expenses": "И доходы, и расходы равны нулю. Пропуск создания круговой диаграммы.",
    "plot_invalid_data": "Доходы и расходы должны быть списками",
    "plot_month_saved": "График за месяц сохранен как month_plot.png",

    # SSH и команды
    "ssh_sudo_forbidden": "Использование команды 'sudo' запрещено.",
    "ssh_command_result": "Результат выполнения команды:\n\n```{stdout}```",
    "ssh_command_error": "Ошибка выполнения команды:\n\n```{stderr}```",
    "ssh_error": "Произошла ошибка при выполнении SSH команды",
    
    # Логи
    "log_header": "Последние записи журнала:",
    "log_cleaned": "Журналы старше 3 дней удалены",

    # Задачи
    "task_none": "У вас нет задач",
    "task_list_title": "Список задач",
    "task_error": "Произошла ошибка",
    "task_deleted": "Задача `{task}` удалена",
    "task_completed": "Задача `{task}` выполнена",
    "task_invalid_format": "Некорректный формат ввода",
    "task_added": "Задача добавлена",
    "task_not_found": "Задача не найдена",
    "task_index_required": "Необходимо указать индекс задачи",
    "task_button_complete": "✅ Выполнить",
    "task_button_delete": "❌ Удалить",
    "task_button_back": "⬅️ Назад к списку",
    "task_button_add": "➕ Добавить задачу",
    "task_button_confirm": "✅ Создать",
    "task_button_cancel": "❌ Отменить",
    "task_completed_short": "Задача выполнена!",
    "task_deleted_short": "Задача удалена!",
    "task_added_short": "Задача добавлена!",
    "task_completed_message": "✅ Задача `{task}` отмечена как выполненная",
    "task_deleted_message": "❌ Задача `{task}` удалена",
    "task_enter_title": "📝 *Введите заголовок* для новой задачи:",
    "task_enter_description": "✏️ *Введите описание* для задачи:",
    "task_title_selected": "📋 Заголовок: *{title}*",
    "task_preview": "📋 Предпросмотр задачи",
    "task_preview_title": "Заголовок",
    "task_preview_description": "Описание",
    "task_confirm_prompt": "Подтвердите создание задачи:",
    "task_added_success": "✅ Задача успешно добавлена!",
    "task_add_cancelled": "❌ Создание задачи отменено",

    # VPS статистика
    "vps_info_title": "Информация о VPS",
    "vps_cpu": "Процессор",
    "vps_ram": "ОЗУ",
    "vps_disk": "Диск",
    "vps_general_stats": "Общая статистика",
    "vps_sites": "Сайтов",
    "vps_domains": "Доменов",
    "vps_ftp": "FTP",
    "vps_databases": "Баз данных",
    "vps_mailboxes": "Почтовых ящиков",
    "vps_tariff": "Тариф",
    "vps_cost": "Стоимость",
    "vps_rub_per_day": "руб в день",
    "vps_rub_per_month": "руб в месяц",
    "vps_rub_per_year": "руб в год",
    "vps_balance": "Баланс",
    "vps_rub": "руб",
    "vps_paid_for": "Оплачено на",
    "vps_days": "дней",
    "vps_load": "Загрузка",
    "vps_uptime": "Время работы",
    "vps_hours": "часов",
    "vps_error": "Произошла ошибка при получении данных о VPS",   
}