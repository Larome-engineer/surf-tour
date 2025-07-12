from datetime import datetime

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.date_utils import DAYS_RU, MONTHS_RU


def user_main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="💻 Мой аккаунт", callback_data="UserAccount"),
        InlineKeyboardButton(text="🏄 Список серф-уроков", callback_data="AllLessonsWithFreePlaces"),
        InlineKeyboardButton(text="🏕 Список туров", callback_data='AllToursWithFreePlaces'),
        width=1
    ).as_markup()


def user_account_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="🏕 Список моих туров", callback_data='UpcomingUserTours'),
        InlineKeyboardButton(text="🏄 Список моих уроков", callback_data='UpcomingUserLessons'),
        InlineKeyboardButton(text="♻️ Изменить мои данные", callback_data="UserChangeData"),
        InlineKeyboardButton(text="🔙", callback_data='BackToUserMainMenu'),
        width=1
    ).as_markup()


def confirm_booking(callback_text):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=callback_text),
        InlineKeyboardButton(text="❌ Отмена", callback_data='BackToUserMainMenu')
    ).as_markup()


def generate_keyboard(list_of_values: list = None, value_key: str = None, callback: str = None,
                      back_callback: str = None, text: str = None):
    keyboard = InlineKeyboardBuilder()
    if list_of_values is None:
        keyboard.row(InlineKeyboardButton(text=text, callback_data=f'{callback}{value_key}'))
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data=back_callback))
        return keyboard.as_markup()

    for value in list_of_values:
        keyboard.row(InlineKeyboardButton(
            text=value[value_key],
            callback_data=f"{callback}{value[value_key]}")
        )
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=back_callback))
    return keyboard.as_markup()


def cancel_or_back_to(text, callback: str):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text, callback_data=callback),
        width=1
    ).as_markup()


def yes_or_not(text_yes, callback_yes, text_no, callback_no):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text_yes, callback_data=callback_yes),
        InlineKeyboardButton(text=text_no, callback_data=callback_no)
    )


def generate_keyboard2(list_of_text: list[str], list_of_callback: list[str], additional_callback: str = None):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(list_of_callback)):
        keyboard.row(
            InlineKeyboardButton(
                text=list_of_text[i],
                callback_data=f"{list_of_callback[i]}" if additional_callback is None else f"{list_of_callback[i]}{additional_callback}"
            )
        )
    return keyboard.as_markup()


def generate_lesson_kb(lessons, callback, back_callback):
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
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))
    return builder.as_markup()


def disable_notifications():
    return (
        InlineKeyboardBuilder()
        .row(InlineKeyboardButton(text="❎ Отключить уведомления", callback_data="DisableNotifications"))
    ).as_markup()


def build_upcoming_lessons_pagination_keyboard(
        lessons: list,
        page: int = 0,
        items_per_page: int = 2,
        callback: str = None,
        back_callback: str = None
):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    page_items = lessons[start:end]

    for l in page_items:
        date = datetime.strptime(l['start_date'], "%d.%m.%Y")
        label = f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {l['time']}"
        keyboard.button(
            text=label,
            callback_data=f"{callback}{l['unicode']}"
        )
    keyboard.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"UpcomingUserList_page:{page - 1}"
            )
        )

    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(
                text="🔙 МЕНЮ",
                callback_data=back_callback
            )
        )

    if end < len(lessons):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"UpcomingUserList_page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()


def build_lessons_pagination_keyboard(
        lessons: list,
        page: int = 0,
        items_per_page: int = 2,
        callback: str = None,
        back_callback: str = None
):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    page_items = lessons[start:end]

    for l in page_items:
        date = datetime.strptime(l['start_date'], "%d.%m.%Y")
        label = f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {l['time']}"
        keyboard.button(
            text=label,
            callback_data=f"{callback}{l['unicode']}"
        )
    keyboard.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"AllToursUserList_page:{page - 1}"
            )
        )

    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(
                text="🔙 МЕНЮ",
                callback_data=back_callback
            )
        )

    if end < len(lessons):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"AllToursUserList_page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()


def build_tours_pagination_keyboard(
        list_of_tours: list = None,
        value_key: str = "name",
        callback: str = None,
        back_callback: str = None,
        back_text: str = "🔙",
        row_width: int = 1,
        page: int = 0,
        items_per_page: int = 2
):
    keyboard = InlineKeyboardBuilder()

    if list_of_tours is None or len(list_of_tours) == 0:
        keyboard.row(
            InlineKeyboardButton(
                text="❌ Туров нет",
                callback_data="UserAccount"
            )
        )
        if back_callback:
            keyboard.row(
                InlineKeyboardButton(
                    text=back_text,
                    callback_data=back_callback
                )
            )
        return keyboard.as_markup()

    # Срез по странице
    start = page * items_per_page
    end = start + items_per_page
    page_items = list_of_tours[start:end]

    for tour in page_items:
        label = f"{tour[value_key]} | {tour.get('start_date', '')}"
        keyboard.button(
            text=label,
            callback_data=f"{callback}{tour[value_key]}"
        )
    keyboard.adjust(row_width)

    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{callback}page:{page - 1}"
            )
        )

    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(
                text="🔙 МЕНЮ",
                callback_data=back_callback
            )
        )

    if end < len(list_of_tours):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"{callback}page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()


def build_tours_upcoming_pagination_keyboard(
        list_of_tours: list = None,
        value_key: str = "name",
        callback: str = None,
        back_callback: str = None,
        back_text: str = "🔙",
        row_width: int = 1,
        page: int = 0,
        items_per_page: int = 2
):
    keyboard = InlineKeyboardBuilder()

    if list_of_tours is None or len(list_of_tours) == 0:
        keyboard.row(
            InlineKeyboardButton(
                text="❌ Туров нет",
                callback_data="UserAccount"
            )
        )
        if back_callback:
            keyboard.row(
                InlineKeyboardButton(
                    text=back_text,
                    callback_data=back_callback
                )
            )
        return keyboard.as_markup()

    # Срез по странице
    start = page * items_per_page
    end = start + items_per_page
    page_items = list_of_tours[start:end]

    for tour in page_items:
        label = f"{tour[value_key]} | {tour.get('start_date', '')}"
        keyboard.button(
            text=label,
            callback_data=f"{callback}{tour[value_key]}"
        )
    keyboard.adjust(row_width)

    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{callback}page:{page - 1}"
            )
        )

    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(
                text="🔙 МЕНЮ",
                callback_data=back_callback
            )
        )

    if end < len(list_of_tours):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"{callback}page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()
