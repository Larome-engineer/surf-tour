from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from utils.date_utils import DAYS_RU, MONTHS_RU


def user_main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Мой аккаунт", callback_data="UserAccount"),
        InlineKeyboardButton(text="Список серф-уроков", callback_data="AllLessonsWithFreePlaces"),
        InlineKeyboardButton(text="Список доступных туров", callback_data='AllToursWithFreePlaces'),
        width=1
    )


def user_account_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Список моих туров", callback_data='UpcomingUserTours'),
        InlineKeyboardButton(text="Список моих уроков", callback_data='UpcomingUserLessons'),
        InlineKeyboardButton(text="Изменить мои данные", callback_data="UserChangeData"),
        InlineKeyboardButton(text="Назад", callback_data='BackToUserMainMenu'),
        width=1
    )


def confirm_booking(callback_text):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Подтвердить", callback_data=callback_text),
        InlineKeyboardButton(text="Отмена", callback_data='BackToUserMainMenu')
    )


def generate_keyboard(list_of_values: list = None, value_key: str = None, callback: str = None,
                      back_callback: str = None, text: str = None):
    keyboard = InlineKeyboardBuilder()
    if list_of_values is None:
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f'{callback}{value_key}'))
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data=back_callback))
        return keyboard

    for value in list_of_values:
        keyboard.row(InlineKeyboardButton(
            text=value[value_key],
            callback_data=f"{callback}{value[value_key]}")
        )
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return keyboard


def cancel_or_back_to(text, callback: str):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text, callback_data=callback),
        width=1
    )


def yes_or_not(text_yes, callback_yes, text_no, callback_no):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text_yes, callback_data=callback_yes),
        InlineKeyboardButton(text=text_no, callback_data=callback_no)
    )


async def generate_keyboard2(list_of_text: list[str], list_of_callback: list[str], additional_callback: str = None):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(list_of_callback)):
        keyboard.row(
            InlineKeyboardButton(
                text=list_of_text[i],
                callback_data=f"{list_of_callback[i]}" if additional_callback is None else f"{list_of_callback[i]}{additional_callback}"
            )
        )
    return keyboard.as_markup()


async def generate_lesson_kb(lessons, callback, back_callback):
    builder = InlineKeyboardBuilder()
    for lsn in lessons:
        date = datetime.strptime(lsn['start_date'], "%d.%m.%Y")
        type_lsn_text = lsn['type'].split(" ")
        builder.row(
            InlineKeyboardButton(
                text=f"{type_lsn_text[0][:3]}.{type_lsn_text[1]} | "
                     f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | "
                     f"{lsn['time']}",
                callback_data=f"{callback}{lsn['unicode']}"
            )
        )
    builder.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return builder.as_markup()
