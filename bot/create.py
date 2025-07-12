from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from tortoise import Tortoise

from config import BOT_TOKEN, DB_URL

# Сохранение payload перед покупкой
# {user_id: {info1: ..., info2: ..., ...}}
payment_payload = {}

surf_bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

admin_commands = [
    BotCommand(command="admin", description="🏠 Панель администратора"),
]

user_commands = [
    BotCommand(command="start", description="🤖 Начало работы с ботом")
]


async def init_db():
    if not Tortoise._inited:
        await Tortoise.init(
            db_url=DB_URL,
            modules={"models": ["database.models"]}
        )
        await Tortoise.generate_schemas()
