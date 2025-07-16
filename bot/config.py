import logging
import os
from logging.handlers import RotatingFileHandler

import yaml
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

with open(os.getenv('SURF_YAML')) as yam:
    YAML = yaml.safe_load(yam)

CONFIG_PATH = YAML['config']
BOT_TOKEN = YAML['telegram']['token']
DB_URL = f"sqlite:///{YAML['database']['path']}"
ADMINS = YAML['telegram']['admins']
PROVIDER_TOKEN = YAML['telegram']['payment_provider_token']
NOTIFICATION_CHAT = YAML['telegram']['notification_chat']

WEBHOOK_DOMAIN = YAML['telegram']['webhook']['domain']
WEBHOOK_PATH = YAML['telegram']['webhook']['path']
WEBAPP_PORT=YAML['telegram']['webapp']['port']
WEBAPP_HOST=YAML['telegram']['webapp']['host']


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(CONFIG_PATH, maxBytes=5_000_000, backupCount=5),
        logging.StreamHandler()
    ],
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
