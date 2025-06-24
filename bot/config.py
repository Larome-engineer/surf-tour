import os

import yaml
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

with open(os.getenv('YML_CONF')) as yam:
    YAML = yaml.safe_load(yam)

BOT_TOKEN = YAML['telegram']['token']
DB_URL = f"sqlite:///{YAML['database']['path']}"
ADMINS = YAML['telegram']['admins']
