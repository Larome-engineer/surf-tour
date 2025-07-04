import logging
import os
from logging.handlers import RotatingFileHandler

import yaml
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

with open(os.getenv('YML_CONF')) as yam:
    YAML = yaml.safe_load(yam)

BOT_TOKEN = YAML['telegram']['token']
DB_URL = f"sqlite:///{YAML['database']['path']}"
ADMINS = YAML['telegram']['admins']
PROVIDER_TOKEN = YAML['telegram']['payment_provider_token']

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler("/home/roman/logs/service.log", maxBytes=5_000_000, backupCount=5),
        logging.StreamHandler()
    ],
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
