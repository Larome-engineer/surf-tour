from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from tortoise import Tortoise

from config import BOT_TOKEN, DB_URL

surf_bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

admin_commands = [

]

user_commands = [

]


async def init_db():
    if not Tortoise._inited:
        await Tortoise.init(
            db_url=DB_URL,
            modules={"models": ["database.models"]}
        )
        await Tortoise.generate_schemas()
