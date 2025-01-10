# Secretary Bot

## Description
This project is a Telegram bot that acts as a personal secretary. It helps automate various tasks such as balance management, report sending, notifications, and much more. The bot is designed to simplify daily tasks and improve productivity.

## Languages
This file on another languages:
- [Russian](./README.md)
- [English](./README.en.md)

## Features
### Commands
- `/start` - Welcome message.
- `/help` - List of available commands.
- `/call` <message> - Send an anonymous message to the bot owner.
- `/report` - Monthly balance report.
- `/balance` - Show current balance.
- `/balance <number>` - Change balance by the specified number.
- `/notification <date> <time> <message>` - Create a notification.
- `/notification` - Show the list of notifications.
- `/notification delete <number>` - Delete a notification by number.
- `/task <title> <message>` - Add a task.
- `/task` - Show the list of tasks.
- `/task delete <number>` - Delete a task by number.
- `/email <message>` - Send a message to the email.
- `/email` - Show the list of email messages.
- `/save` - Save a file on the web server.
- `/download <name>` - Download a file from the server.
- `/delete <name>` - Delete a file from the server.
- `/files` - Show the list of files.
- `/share` - Share a file.
- `/pdownload <name>` - Download a public file.
- `/pdelete <name>` - Delete a public file.
- `/pfiles` - List of public files.
- `/log` - Show the last 25 lines of logs.
- `/ssh <command>` - Execute a command on the server.
- `/stats` - Show Beget statistics.

### Automatic Tasks
- Daily task check.
- Monthly balance report sending.

## Installation
1. Clone the repository:
```sh
git clone https://github.com/ivanvit100/secretary_bot
cd secretary_bot
```
2. Create and activate a virtual environment:
```sh
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```sh
pip install -r requirements.txt
```
4. Create a `.env` file and add your bot token, user ID, email login and password, SMTP and IMAP servers, and API server link:
```
BOT_TOKEN = your_bot_token
USER_ID = your_user_id

EMAIL_ADDRESS = email@example.com
EMAIL_PASSWORD = your_password

SMTP_ADDRESS = smtp.example.com
IMAP_ADDRESS = imap.example.com

VPS_USER_STATS = https://...
```
5. Edit the configs and `secretary.service`.
6. Set up and start the systemd service:
```sh
sudo cp secretary.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable secretary.service
sudo systemctl start secretary.service
```

## Usage
After starting the bot, you can use the commands listed above to interact with the bot. The bot will automatically perform daily and monthly tasks.

## License
This project is licensed under the [MIT License](./LICENSE).

## Contacts
If you have any questions or suggestions, you can contact the project author via [GitHub](https://github.com/ivanvit100/secretary_bot/issues).