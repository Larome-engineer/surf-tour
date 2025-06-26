from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def user_main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Мой аккаунт", callback_data="useraccount"),
    InlineKeyboardButton(text="Список туров", callback_data='tourlistforuser'),
    InlineKeyboardButton(text="Забронировать тур", callback_data='userbooktour'),
    width = 1
    )

def user_account_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Список моих туров", callback_data='upcomingusertourlist'),
        InlineKeyboardButton(text="Изменить мои данные", callback_data="userchangedata"),
        InlineKeyboardButton(text="Назад", callback_data='backtousermenu'),
        width = 1
    )

def cancel_book():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Отменить бронирование", callback_data='backtousermenu'),
        width = 1
    )

def confirm_booking():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Подтвердить", callback_data='applyuserbooking'),
        InlineKeyboardButton(text="Отмена", callback_data='backtousermenu')
    )
