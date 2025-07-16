from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.handler_utils import safe_send_all, safe_send_copy_all
from utils.btn_utils import btn_perform
from utils.date_utils import perform_date, safe_parse_date
from utils.plural_form import get_plural_form

async def notify_places_lesson(lesson, users_list, places: int):
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


async def notify_places_tour(tour, users_list, places: int):
    text = (
        f"🔥 ДОБАВЛИСЬ МЕСТА! 🔥\n"
        f"{tour['name']}\n{btn_perform(tour['dest'], tour['start_date'].strftime('%d.%m.%Y'), tour['time'], is_lesson=False)}"
        f"Добавилось: {places} {get_plural_form(places, 'Место', 'Места', 'Мест')}\n\n"
        f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️",
    )
    tour_perform = btn_perform(
        tour['dest'],
        tour['start_date'],
        tour['time'],
        end_date=tour['end_date'],
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
        f"\n\n⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️"
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
        tour['start'].date().strftime('%d.%m.%Y'),
        tour['time'].date().strftime('%d.%m.%Y'),
        end_date=tour['end'],
        is_lesson=False
    )

    text = (
        f"🏕 ОТКРЫЛСЯ НОВЫЙ ТУР! 🏕\n"
        f"{tour['name']}\n"
        f"{tour['dest']}\n"
        f"{perform_date(tour['start'].strftime('%d.%m.%Y'), tour['time'])}"
        f"\n\n⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️"
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
