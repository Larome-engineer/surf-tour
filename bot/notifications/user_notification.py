from datetime import datetime

from bot.create import surf_bot
from bot.keyboards.admin import one_button_callback
from database import service
from utils.date_utils import MONTHS_RU, DAYS_RU
from utils.plural_form import get_plural_form


async def notify_about_places_lesson(lesson_code, users_list, places: int):
    send = 0
    not_send = 0
    lesson = await service.get_lesson_by_code(lesson_code)
    date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")
    lsn_type = lesson['type'].split(" ")
    lsn = f"{lsn_type[0][:4]}.{lsn_type[1]} | {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}"
    for u in users_list:
        try:
            await surf_bot.send_message(
                chat_id=u,
                text=f"🔥 ДОБАВЛИСЬ МЕСТА! 🔥\n"
                     f"{lsn}\n"
                     f"Добавилось: {places} {get_plural_form(places, 'Место', 'Места', 'Мест')}\n\n"
                     f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️",
                reply_markup=one_button_callback(lsn, f"UserMoreAboutLesson_{lesson['unicode']}").as_markup()
            )
            send += 1
        except Exception as ex:
            not_send += 1
            continue
    return send, not_send


async def notify_about_places_tour(tour_name, users_list, places: int):
    send = 0
    not_send = 0
    tour = await service.get_tour_by_name(tour_name)
    date = datetime.strptime(tour['start_date'], "%d.%m.%Y")
    for u in users_list:
        try:
            await surf_bot.send_message(
                chat_id=u,
                text=f"🔥 ДОБАВЛИСЬ МЕСТА! 🔥\n"
                     f"{tour['dest']} | {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {tour['time']}\n"
                     f"Добавилось: {places} {get_plural_form(places, 'Место', 'Места', 'Мест')}\n\n"
                     f"⬇️ <b>ПОСМОТРЕТЬ</b> ⬇️",
                reply_markup=one_button_callback(tour_name, f"MoreAboutTour_{tour_name}").as_markup()
            )
            send += 1
        except Exception as ex:
            not_send += 1
            continue
    return send, not_send
