from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from utils.date_utils import MONTHS_RU, DAYS_RU


def main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="🏕 | 🏄 | 🗺", callback_data='ToursLessonsDirections'),
        InlineKeyboardButton(text="👨🏻‍💻", callback_data='Users'),
        InlineKeyboardButton(text="📦", callback_data="DatabaseExport"),
        width=1
    ).as_markup()


def tour_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="➕ Добавить тур", callback_data='AddTour'),
        InlineKeyboardButton(text="📋 Список туров", callback_data='AllTourList'),
        InlineKeyboardButton(text="🗺 Тур по направлению", callback_data='TourByDirection'),
        InlineKeyboardButton(text="📘 Забронированные туры", callback_data='BookedTours'),
        InlineKeyboardButton(text="🔙", callback_data='BackToTourLessonsDirections'),
        width=1
    ).as_markup()


def lesson_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="➕ Добавить урок", callback_data='AddLesson'),
        InlineKeyboardButton(text="🧬 Добавить тип урока", callback_data="AddLessonType"),
        InlineKeyboardButton(text="📋 Список уроков", callback_data='AllLessonList'),
        InlineKeyboardButton(text="🗺 Урок по направлению", callback_data='LessonByDirection'),
        InlineKeyboardButton(text="📘 Забронированные уроки", callback_data='BookedLessons'),
        InlineKeyboardButton(text="🔙", callback_data='BackToTourLessonsDirections'),
        width=1
    ).as_markup()


def direct_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="➕ Добавить направление", callback_data='AddDirection'),
        InlineKeyboardButton(text="🗺 Доступные направления", callback_data='DirectionsList'),
        InlineKeyboardButton(text="🗑 Удалить направление", callback_data='DeleteDirection'),
        InlineKeyboardButton(text="🔙", callback_data='BackToTourLessonsDirections'),
        width=1
    ).as_markup()


def apply_delete_dir():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Да", callback_data='DeleteDir_apply'),
        InlineKeyboardButton(text="Отмена", callback_data='DeleteDir_decline'),
    ).as_markup()


def tours_lessons_directions():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="🏕 Туры 🏕", callback_data='Management_tour'),
        InlineKeyboardButton(text="🏄 Уроки 🏄", callback_data='Management_lesson'),
        InlineKeyboardButton(text="🗺 Направления 🗺", callback_data='Management_direct'),
        InlineKeyboardButton(text="🔙", callback_data='BackToAdminMenu'),
        width=1
    ).as_markup()


###### USER ######
def user_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="📩 Рассылка", callback_data='UserMailing'),
        InlineKeyboardButton(text="📚 Список пользователей", callback_data='UsersList'),
        InlineKeyboardButton(text="👨🏻‍💻 Информация о пользователе", callback_data='UsersInfo'),
        InlineKeyboardButton(text="🔙", callback_data='BackToAdminMenu'),
        width=1
    ).as_markup()


def confirm_mailing():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Отправить", callback_data='send_mailing'),
        InlineKeyboardButton(text="Отмена", callback_data='decline_mailing')
    ).as_markup()


def user_info():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="🆔 Telegram ID", callback_data='SearchByTgId'),
        InlineKeyboardButton(text="✉️/📞 Почта или номер телефона", callback_data='SearchByPhoneOrEmail'),
        InlineKeyboardButton(text="🔙", callback_data='BackToUsersMenu'),
        width=1
    ).as_markup()


def back_to(text, callback: str):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text, callback_data=callback),
        width=1
    ).as_markup()


def one_button_callback(text, callback):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text, callback_data=callback),
        width=1
    ).as_markup()


def any_button_kb(text, callback):
    builder = InlineKeyboardBuilder()
    for i in range(len(text)):
        builder.row(InlineKeyboardButton(text=text[i], callback_data=callback[i]))
    return builder.as_markup()


def simple_build_dynamic_keyboard(
        list_of_values: list = None,
        value_key: str = None,
        callback: str = None,
        back_callback: str = None,
        text: str = None,
        back_text: str = "🔙",
        row_width: int = 1
):
    keyboard = InlineKeyboardBuilder()

    if list_of_values is None:
        keyboard.row(InlineKeyboardButton(
            text=text,
            callback_data=f'{callback}{value_key}'
        ))
        keyboard.row(InlineKeyboardButton(
            text=back_text,
            callback_data=back_callback
        ))
        return keyboard.as_markup()

    # Генерация кнопок из списка
    buttons = [
        InlineKeyboardButton(
            text=value[value_key] if value_key else str(value),
            callback_data=f"{callback}{value[value_key] if value_key else str(value)}"
        )
        for value in list_of_values
    ]
    keyboard.add(*buttons)
    keyboard.adjust(row_width)

    # Кнопка назад
    if back_callback:
        keyboard.row(InlineKeyboardButton(
            text=back_text,
            callback_data=back_callback
        ))

    return keyboard.as_markup()


def generate_entity_options(list_of_text: list[str], list_of_callback: list[str], entity, entity_key):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(list_of_callback)):
        if list_of_text[i] != "🔙" and not list_of_callback[i].startswith("All") and not list_of_callback[i].startswith("Booked"):
            cb_data = f"{list_of_callback[i]}{entity[entity_key]}"
        else:
            cb_data = f"{list_of_callback[i]}"

        keyboard.row(
            InlineKeyboardButton(
                text=list_of_text[i],
                callback_data=cb_data
            )
        )
    return keyboard.as_markup()


def buttons_by_entity_list_values(entity_list, callback, back_to_callback):
    builder = InlineKeyboardBuilder()
    for entity in entity_list:
        builder.row(InlineKeyboardButton(text=entity.type.capitalize(), callback_data=f"{callback}{entity.type}"))
    builder.row(InlineKeyboardButton(text="🔙", callback_data=back_to_callback))
    return builder.as_markup()


def generate_lesson_kb(lessons, callback, back_callback):
    builder = InlineKeyboardBuilder()
    for lsn in lessons:
        date = datetime.strptime(lsn['start_date'], "%d.%m.%Y")
        type_lsn_text = lsn['type'].capitalize().split(" ")
        builder.row(
            InlineKeyboardButton(
                text=f"{type_lsn_text[0][:3]}.{type_lsn_text[1]} | "
                     f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | "
                     f"{lsn['time']}",
                callback_data=f"{callback}{lsn['unicode']}"
            )
        )
    builder.row(InlineKeyboardButton(text="🔙", callback_data=back_callback))
    return builder.as_markup()


def build_lessons_pagination_keyboard(
        lessons: list,
        page: int = 0,
        items_per_page: int = 2,
        back_callback: str = None
):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    page_items = lessons[start:end]

    for l in page_items:
        date = l['start_date']
        label = f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {l['time']}"
        keyboard.button(
            text=label,
            callback_data=f"InfoAboutLesson_{l['unicode']}"
        )
    keyboard.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"LessonsList_page:{page - 1}"
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
                callback_data=f"LessonsList_page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()


def build_booking_lessons_pagination_keyboard(
        lessons: list,
        page: int = 0,
        items_per_page: int = 2,
        back_callback: str = None
):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    page_items = lessons[start:end]

    for l in page_items:
        date = l['start_date']
        label = f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {l['time']}"
        keyboard.button(
            text=label,
            callback_data=f"InfoAboutBOOKINGLesson_{l['unicode']}"
        )
    keyboard.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"LessonsBOOKINGList_page:{page - 1}"
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
                callback_data=f"LessonsBOOKINGList_page:{page + 1}"
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
                callback_data="NoTours"
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
        label = f"{tour[value_key]} | {tour.get('start_date', '').strftime('%d.%m.%Y')}"
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


def build_booking_tours_pagination_keyboard(
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
                callback_data="NoTours"
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
        label = f"{tour[value_key]} | {tour.get('start_date', '').strftime('%d.%m.%Y')}"
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


def build_users_pagination_keyboard(
        users: list,
        page: int = 0,
        items_per_page: int = 2,
        back_callback: str = None
):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    page_items = users[start:end]

    for l in page_items:
        label = f"{l['name']} | {l['tg_id']}"
        keyboard.button(
            text=label,
            callback_data=f"InfoAboutUser_{l['tg_id']}"
        )
    keyboard.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"UsersList_page:{page - 1}"
            )
        )

    if back_callback:
        nav_buttons.append(
            InlineKeyboardButton(
                text="🔙 МЕНЮ",
                callback_data=back_callback
            )
        )

    if end < len(users):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"UsersList_page:{page + 1}"
            )
        )
    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard.as_markup()


def yes_or_not(text_yes, callback_yes, text_no, callback_no):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=text_yes, callback_data=callback_yes),
        InlineKeyboardButton(text=text_no, callback_data=callback_no)
    ).as_markup()
