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
2. Run the setup script:
```sh
python setup.py
```
3. During the setup process, the script will:
    - Create necessary directories (`data`, `files`, `public_files`, `documents`)
    - Set up a Python virtual environment
    - Install required packages from [`requirements.txt`](/requirements.txt)
    - Create templet files:
        - `balance.json` - for tracking financial data
        - `tasks.json` - for managing tasks
        - `email.html` - email template
4. When prompted, provide the following information:
```sh
Telegram Bot Token: [Your bot token from @BotFather]
Your Telegram User ID: [Your Telegram user ID]
Email Address: [Email address for sending notifications]
Email Password: [Email password - input will be hidden]
SMTP Server Address: [Press Enter for default (smtp.gmail.com) or enter custom]
IMAP Server Address: [Press Enter for default (imap.gmail.com) or enter custom]
VPS User Stats URL: [URL for VPS statistics]
```
5. Linux users will be asked if they want to install a systemd service:
```sh
Do you want to install the secretary.service for automatic startup? (y/n):
```
- If you select `y`, the script will:
    - Create a `systemd` service file
    - Ask for `sudo` password to install the service
    - Enable the service to start on system boot
    - Start the service immediately
6. After successful setup, activate the environment and start the bot:
- For Linux/Mac:
```sh
source venv/bin/activate
python main.py
```
- For Windows:
```cmd
.\venv\Scripts\activate
python main.py
```

## Usage
After starting the bot, you can use the commands listed above to interact with the bot. The bot will automatically perform daily and monthly tasks.

## License
This project is licensed under the [MIT License](./LICENSE).

## Contacts
If you have any questions or suggestions, you can contact the project author via [GitHub](https://github.com/ivanvit100/secretary_bot/issues).