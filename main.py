import telebot
import logging
import config
import os
from modules.functions import main
from dotenv import load_dotenv
from i18n import _

#########################
#                       #
#        CONFIGS        #
#                       #
#########################

load_dotenv()

logging.basicConfig(
    filename='./secretary.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

imports = {}

if config.MODULES["balance"]:
    from libs.balance import *
    imports["balance"] = True
if config.MODULES["notification"]:
    from libs.notification import *
    imports["notification"] = True
if config.MODULES["support"]:
    from libs.support import *
    imports["support"] = True
if config.MODULES["email"]:
    from libs.email import *
    imports["email"] = True
if config.MODULES["files"]:
    from libs.files import *
    imports["files"] = True
if config.MODULES["task"]:
    from libs.task import *
    imports["task"] = True
if config.MODULES["vps"]:
    from libs.vps import *
    imports["vps"] = True

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

bot = telebot.TeleBot(BOT_TOKEN)

logging.debug('Starting secretary bot')



if __name__ == '__main__':
    main()