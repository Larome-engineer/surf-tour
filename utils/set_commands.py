from aiogram import Bot
from aiogram.types import BotCommandScopeChat

from bot.config import ADMINS
from bot.create import admin_commands, user_commands


async def set_user_commands(bot: Bot, user_id):
    await bot.set_my_commands(
        commands=user_commands,
        scope=BotCommandScopeChat(chat_id=user_id)
    )


async def set_admin_commands(bot: Bot):
    for i in ADMINS:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=int(i))
            )
        except Exception as e:
            continue
