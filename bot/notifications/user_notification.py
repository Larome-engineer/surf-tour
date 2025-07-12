from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.create import surf_bot
from bot.handlers.handler_utils import safe_send_all, safe_send_copy_all
from bot.keyboards.admin import one_button_callback
from database import service
from utils.date_utils import perform_date
from utils.btn_utils import btn_perform
from utils.plural_form import get_plural_form


async def notify_places_lesson(lesson_code, users_list, places: int):
    lesson = await service.get_lesson_by_code(lesson_code)

    lsn = btn_perform(
        lesson['type'],
        lesson['start_date'],
        lesson['time']
    )

    text = (
        f"🔥 ДОБАВЛИСЬ МЕСТА! 🔥\n"
        f"{lsn}\n"
        f"Добавилось: {places} {get_plural_form(places, 'Место', 'Места', 'Мест')}\n\n"
        f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=lsn, callback_data=f"UserMoreAboutLesson_{lesson['unicode']}"))
    builder.row(InlineKeyboardButton(text="Отключить уведомления", callback_data="DisableNotifications"))
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="UserAccount"))

    send, not_send = await safe_send_all(
        text=text,
        users=users_list,
        reply_markup=builder.as_markup()

    )

    return send, not_send


async def notify_places_tour(tour_name, users_list, places: int):
    tour = await service.get_tour_by_name(tour_name)

    text = (
        f"🔥 ДОБАВЛИСЬ МЕСТА! 🔥\n"
        f"{tour_name}\n{btn_perform(tour['dest'], tour['start'], tour['time'], is_lesson=False)}"
        f"Добавилось: {places} {get_plural_form(places, 'Место', 'Места', 'Мест')}\n\n"
        f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️",
    )
    tour_perform = btn_perform(
        tour['dest'],
        tour['start'],
        tour['time'],
        end_date=tour['end'],
        is_lesson=False
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=tour_perform, callback_data=f"MoreAboutTour_{tour['name']}"))
    builder.row(InlineKeyboardButton(text="Отключить уведомления", callback_data="DisableNotifications"))
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="UserAccount"))

    send, not_send = await safe_send_all(
        text=text,
        users=users_list,
        reply_markup=builder.as_markup()
    )

    return send, not_send


async def notify_about_lesson(lesson: dict, users):
    lsn = btn_perform(
        lesson['type'],
        lesson['start'],
        lesson['time']
    )

    text = (
        f"🏄 ОТКРЫЛСЯ НОВЫЙ УРОК! 🏄\n"
        f"{lesson['type']}\n"
        f"{lesson['dest']}\n"
        f"{perform_date(lesson['start'], lesson['time'])}"
        f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=lsn, callback_data=f"UserMoreAboutLesson_{lesson['unicode']}"))
    builder.row(InlineKeyboardButton(text="Отключить уведомления", callback_data="DisableNotifications"))
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="UserAccount"))

    send, not_send = await safe_send_all(
        text=text,
        users=users,
        reply_markup=builder.as_markup()
    )

    return send, not_send


async def notify_about_tour(tour, users):
    tour_perform = btn_perform(
        tour['dest'],
        tour['start'],
        tour['time'],
        end_date=tour['end'],
        is_lesson=False
    )

    text = (
        f"🏕 ОТКРЫЛСЯ НОВЫЙ ТУР! 🏕\n"
        f"{tour['name']}\n"
        f"{tour['dest']}\n"
        f"{perform_date(tour['start'], tour['time'])}"
        f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=tour_perform, callback_data=f"MoreAboutTour_{tour['name']}"))
    builder.row(InlineKeyboardButton(text="Отключить уведомления", callback_data="DisableNotifications"))
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="UserAccount"))

    send, not_send = await safe_send_all(
        text=text,
        users=users,
        reply_markup=builder.as_markup()
    )

    return send, not_send

async def mailing_action(from_chat, message, users):
    send, not_send = await safe_send_copy_all(
        from_chat=from_chat,
        message=message,
        users=users
    )
    return send, not_send


