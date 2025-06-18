messages = {
    # Command descriptions
    "cmd_start": "Welcome! I'm a personal secretary bot.\nI won't reveal my boss, but if you want one like me, type /link.\nIf you want to know what I can do, type /help.\nTo send an anonymous message to my boss, type /call.",
    "cmd_help_title": "Available commands",
    
    # Public commands
    "public_commands": "Public commands:",
    "cmd_help": "- /help - list of commands",
    "cmd_call": "- /call - write to the bot owner",
    "cmd_pfiles": "- /pfiles - view list of public files",
    "cmd_pdownload": "- /pdownload <name> - download a public file",
    "cmd_link": "- /link - link to the bot's source code",
    "cmd_language": "- /language - change bot language",
    
    # Private commands
    "private_commands": "Private commands:",
    "cmd_report": "- /report - balance report",
    "cmd_balance": "- /balance - current balance",
    "cmd_balance_change": "- /balance <number> - change balance by number",
    "cmd_notification_add": "- /notification <date> <time> <message> - create notification",
    "cmd_notification_list": "- /notification - list of notifications",
    "cmd_notification_delete": "- /notification delete <number> - delete a notification",
    "cmd_task_add": "- /task <message> - add a task",
    "cmd_task_list": "- /task - list of tasks",
    "cmd_task_delete": "- /task delete <number> - delete a task",
    "cmd_email_send": "- /email <address> <message> - send an email message",
    "cmd_email_list": "- /email - list of email messages",
    "cmd_save": "- /save - save a file on the server",
    "cmd_share": "- /share <name> - share a file",
    "cmd_download": "- /download <name> - download a file",
    "cmd_delete": "- /delete <name> - delete a file",
    "cmd_pdelete": "- /pdelete <name> - delete a public file",
    "cmd_log": "- /log - activity log",
    "cmd_ssh": "- /ssh <command> - execute a command on the server",
    "cmd_stats": "- /stats - Beget statistics",
    "cmd_language": "- /language - change bot language",
    
    # Common messages
    "no_permission": "You don't have permission to execute this command",
    "error_occurred": "An error occurred",
    "file_saved": "File saved",
    "file_deleted": "File deleted",
    "message_sent": "Message sent",
    "files_list_title": "Files list",
    "task_added": "Task added",
    "task_completed": "Task completed",
    "task_deleted": "Task deleted",
    
    # Daily report
    "daily_summary_title": "Daily summary",
    "daily_balance": "Balance",
    "daily_saldo": "Saldo",
    "daily_tasks": "Tasks",
    "daily_completed": "Completed this month",
    
    # Startup
    "secretary_started": "Secretary started",
    
    # Language
    "language_changed": "Language changed to English",
    "language_select": "Select language:",

    # Main balance messages
    "balance_current_month": "Current month: {month}\n\nYour balance: `{balance}`\nSaldo: `{saldo}`",
    "balance_updated": "Balance updated: `{value}`",
    "balance_invalid_format": "Invalid parameter format",
    
    # Balance report
    "balance_report_title": "Balance Report",
    "balance_forecast_current": "Forecasted balance for current month: `{value}`",
    "balance_forecast_saldo_current": "Forecasted saldo for current month: `{value}`",
    "balance_forecast_next": "Forecasted balance for next month: `{value}`",
    "balance_forecast_saldo_next": "Forecasted saldo for next month: `{value}`",
    "balance_current_income": "Current income: `{value}`",
    "balance_current_expenses": "Current expenses: `{value}`",
    "balance_avg_year": "Average yearly balance: `{value}`",
    "balance_avg_saldo_year": "Average yearly saldo: `{value}`",
    "balance_max_year": "Maximum yearly balance: `{value}` ({month})",
    "balance_min_year": "Minimum yearly balance: `{value}` ({month})",
    "balance_total_year": "Total yearly income: `{value}`",
    "balance_report_error": "An error occurred while sending the report.",
    
    # Balance reset
    "balance_reset_title": "Monthly Balance Reset",
    "balance_reset_message": "Balance at the beginning of the month: {value} (carried over from {month})",
    "balance_reset_saldo": "Saldo reset to zero",
    "balance_reset_daily": "Daily income and expenses reset",
    "balance_reset_month_not_found": "Error: month {month} not found in balance file",
    "balance_reset_error": "An error occurred during balance reset: {error}",

    # Email messages
    "email_no_messages": "No new messages",
    "email_list_title": "List of recent messages for `{email}`:",
    "email_read_command": "Read: /email_read_{index}",
    "email_sent_success": "Message sent to email",
    "email_error": "An error occurred while sending the message",
    "email_subject_default": "Message from {name}",
    "email_read_error": "An error occurred while processing the message",
    "email_send_failed": "Failed to send email",

    # File operations
    "file_saved": "File saved",
    "file_error": "An error occurred",
    "files_list_title": "Files list",
    "file_deleted": "File deleted",
    "file_shared": "File moved to public files",
    "file_not_found": "File not found",
    "files_list_empty": "File list is empty",
    "files_list_title": "File List",
    "private_files_title": "Private Files",
    "public_files_title": "Public Files", 
    "prev_page": "Previous",
    "next_page": "Next",
    "page": "Page",
    "of": "of",

    # Notifications
    "notification_alert": "Attention! New notification!",
    "notification_list_title": "Notifications",
    "notification_list_empty": "You don't have any scheduled notifications.",
    "notification_past_error": "Cannot schedule notification in the past: {time}",
    "notification_cancelled": "Notification with index {index} cancelled",
    "notification_invalid_index": "No notification found with index {index}",
    "notification_scheduled": "Notification scheduled for {time}",

    # Plots
    "plot_balance_label": "Balance",
    "plot_saldo_label": "Saldo",
    "plot_month_label": "Month",
    "plot_amount_label": "Amount",
    "plot_balance_title": "Balance and Saldo by Month",
    "plot_income_label": "Income",
    "plot_expenses_label": "Expenses",
    "plot_income_legend": "income",
    "plot_expenses_legend": "expenses",
    "plot_month_stats_title": "Month Statistics",
    
    # Log messages for plots.py
    "plot_balance_saved": "Balance plot saved as balance_plot.png",
    "plot_income_saved": "Income and expenses plot saved as income_expenses_plot.png",
    "plot_zero_income_expenses": "Both income and expenses are zero. Skipping pie chart generation.",
    "plot_invalid_data": "Income and expenses should be lists",
    "plot_month_saved": "Month plot saved as month_plot.png",

    # SSH and commands
    "ssh_sudo_forbidden": "Using 'sudo' command is forbidden.",
    "ssh_command_result": "Command execution result:\n\n```{stdout}```",
    "ssh_command_error": "Command execution error:\n\n```{stderr}```",
    "ssh_error": "An error occurred during SSH command execution",
    
    # Logs
    "log_header": "Recent log entries:",
    "log_cleaned": "Logs older than 3 days have been removed",

    # Tasks
    "task_none": "You don't have any tasks",
    "task_list_title": "Task List",
    "task_error": "An error occurred",
    "task_deleted": "Task `{task}` deleted",
    "task_completed": "Task `{task}` completed", 
    "task_invalid_format": "Invalid input format",
    "task_added": "Task added",
    "task_not_found": "Task not found",
    "task_index_required": "Task index is required",
    "task_button_complete": "✅ Complete",
    "task_button_delete": "❌ Delete",
    "task_button_back": "⬅️ Back to list",
    "task_completed_short": "Task completed!",
    "task_deleted_short": "Task deleted!",
    "task_completed_message": "✅ Task `{task}` marked as completed",
    "task_deleted_message": "❌ Task `{task}` deleted",

    # VPS statistics
    "vps_info_title": "VPS Information",
    "vps_cpu": "CPU",
    "vps_ram": "RAM",
    "vps_disk": "Disk",
    "vps_general_stats": "General Statistics",
    "vps_sites": "Sites",
    "vps_domains": "Domains",
    "vps_ftp": "FTP",
    "vps_databases": "Databases",
    "vps_mailboxes": "Mailboxes",
    "vps_tariff": "Plan",
    "vps_cost": "Cost",
    "vps_rub_per_day": "RUB per day",
    "vps_rub_per_month": "RUB per month",
    "vps_rub_per_year": "RUB per year",
    "vps_balance": "Balance",
    "vps_rub": "RUB",
    "vps_paid_for": "Paid for",
    "vps_days": "days",
    "vps_load": "Load",
    "vps_uptime": "Uptime",
    "vps_hours": "hours",
    "vps_error": "An error occurred while fetching VPS data",
}