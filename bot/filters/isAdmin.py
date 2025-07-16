from bot.config import ADMINS
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMINS