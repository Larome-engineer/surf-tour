from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def user_main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Мой аккаунт", callback_data="useraccount"),
    InlineKeyboardButton(text="Список туров", callback_data='usertourlist'),
    InlineKeyboardButton(text="Информация о туре", callback_data="usertourinfo"),
    InlineKeyboardButton(text="Забронировать тур", callback_data='userbooktour'),
    width = 1
    )
