import datetime
import logging

from utils.serializer import *
from . import repository
from .models import *

logger = logging.getLogger(__name__)

# --------------------
# USER
# --------------------
async def create_user(tg_id):
    try:
        await repository.create_user(User(user_tg_id=tg_id))
        logger.info("Добавился новый пользователь:  %s", tg_id)
        return True
    except Exception as e:
        logger.exception("Ошибка в create_user:", e)
        return None


async def get_all_users():
    try:
        users = await repository.get_all_users()
        if not users:
            return None
        result = []
        for u in users:
            result.append(serialize_user(u))
        return result
    except Exception as e:
        logger.exception("Ошибка в get_all_users:", e)
        return None


async def get_user_by_phone_or_email(phone_or_email):
    try:
        user = await repository.get_user_by_phone_or_email(phone_or_email)
        if not user:
            return None
        return serialize_user(user)
    except Exception as e:
        logger.exception("Ошибка в get_user_by_phone_or_email:", e)
        return None


async def get_user_by_tg_id(tg_id):
    try:
        user = await repository.get_user_by_tg_id(tg_id)
        if not user:
            return None
        return serialize_user(user)
    except Exception as e:
        logger.exception("Ошибка в get_user_by_tg_id:", e)
        return None


async def update_user(tg_id, name=None, email=None, phone=None):
    try:
        updated = await repository.update_user(User(
            user_tg_id=tg_id,
            user_name=name,
            user_email=email,
            user_phone=phone
        ))
        logger.info("Пользователь %s обновил данные", tg_id)
        return updated
    except Exception as e:
        logger.exception("Ошибка в update_user:", e)
        return None


async def delete_user_by_tg_id(tg_id):
    try:
        await repository.delete_user_by_tg_id(tg_id)
        logger.info("Удален пользователь:  %s", tg_id)
        return True
    except Exception as e:
        logger.exception("Ошибка в delete_user_by_tg_id:", e)
        return None


async def get_all_users_ids():
    try:
        ids = await repository.get_all_users_ids()
        if not ids:
            return None
        return list(ids)
    except Exception as e:
        logger.exception("Ошибка в get_all_users_ids:", e)
        return None


async def get_upcoming_user_tours(tg_id):
    try:
        user_tours = await repository.get_upcoming_user_tours(tg_id)
        if not user_tours:
            return None

        result = []
        for ut in user_tours:
            payment = await repository.get_user_tour_payment(ut.user.user_id, ut.tour.tour_id)
            result.append(serialize_tour(ut.tour, payment))
        return result

    except Exception as e:
        logger.exception("Ошибка в get_upcoming_user_tours:", e)
        return None


async def get_user_lesson_details(tg_id, code):
    try:
        us = await repository.get_user_lesson_details(tg_id, code)
        if not us:
            return None
        payment = await repository.get_user_lesson_payment(us.user.user_id, us.surf.surf_id)
        return serialize_lesson(us.surf, payment)

    except Exception as e:
        logger.exception("Ошибка в get_user_lesson_details:", e)
        return None


async def get_user_tour_details(tg_id, tour_name):
    try:
        ut = await repository.get_user_tour_details(tg_id, tour_name)
        if not ut:
            return None

        payment = await repository.get_user_tour_payment(ut.user.user_id, ut.tour.tour_id)
        return serialize_tour(ut.tour, payment)
    except Exception as e:
        logger.exception("Ошибка в get_user_tour_details:", e)
        return None


# --------------------
# LESSON
# --------------------
async def create_lesson(desc, places, start, time, duration, price, dest, lesson_type):
    try:
        destination = await repository.get_destination_by_name(dest)
        less_type = await repository.get_lesson_type(lesson_type)
        if destination is None or less_type is None: return None
        unicode = await repository.create_lesson(
            SurfLesson(
                surf_desc=desc,
                surf_places=places,
                surf_duration=duration,
                start_date=start.date().strftime("%d.%m.%Y"),
                start_time=time,
                surf_price=price,
                surf_destination=destination,
                surf_type=less_type
            )
        )
        return True, unicode
    except Exception as e:
        logger.exception("Ошибка в create_lesson:", e)
        return None


async def get_future_paid_lesson(code):
    try:
        lesson =  await repository.get_future_paid_lesson(code)
        if not lesson:
            return None
        return serialize_lesson(surf=lesson)
    except Exception as e:
        logger.exception("Ошибка в get_future_paid_lesson:", e)
        return None



async def get_all_lessons():
    try:
        lessons = await repository.get_all_lessons()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_lessons:", e)
        return None


async def get_all_lessons_by_dest(destination_name):
    try:
        lessons = await repository.get_all_lessons_by_dest(destination_name)
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_lessons_by_dest:", e)
        return None


async def get_all_lessons_with_places():
    try:
        lessons = await repository.get_all_lessons_with_places()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_lessons_with_places:", e)
        return None


async def get_all_lessons_by_date(start_date):
    try:
        lessons = await repository.get_lessons_by_date(start_date)
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_lessons_by_date:", e)
        return None


async def get_future_lessons():
    try:
        lessons = await repository.get_future_lessons()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_lessons_where_start_data_bigger_than_now:", e)
        return None


async def get_all_paid_lesson():
    try:
        lessons = await repository.get_all_paid_lesson()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_paid_lesson:", e)
        return None


async def get_lesson_by_code(code):
    try:
        lesson = await repository.get_lesson_by_code(code)
        if not lesson:
            return None
        return serialize_lesson(surf=lesson)
    except Exception as e:
        logger.exception("Ошибка в get_lesson_by_name:", e)
        return None


async def get_all_booked_lessons():
    try:
        lessons = await repository.get_all_booked_lessons()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]
    except Exception as e:
        logger.exception("Ошибка в get_all_booked_lessons:", e)
        return None


async def get_all_booked_lessons_future():
    try:
        lessons = await repository.get_all_booked_lessons_future()
        if not lessons:
            return None

        result = []
        for l in lessons:
            users = []
            for us in l.user_surfs:
                if us.user:
                    users.append(serialize_user(us.user))
            result.append(serialize_lesson(surf=l, users=users))
        return result
    except Exception as e:
        logger.exception("Ошибка в get_all_booked_lessons_future:", e)
        return None


async def reduce_places_on_lesson(code, count):
    try:
        result = await repository.reduce_places_on_lesson(code, count)
        if result is None:
            logger.exception(f"Тур '{code}' не найден.")
            return None
        if not result:
            logger.exception(f"Нельзя уменьшить места: недостаточно свободных мест в '{code}'.")
            return False
        return True
    except Exception as e:
        logger.exception("Ошибка в reduce_places_on_lesson:", e)
        return None


async def add_places_on_lesson(code, count):
    try:
        result = await repository.add_places_on_lesson(code, count)
        if result is None:
            logger.exception(f"Тур '{code}' не найден.")
            return None
        return True
    except Exception as e:
        logger.exception("Ошибка в add_places_on_lesson:", e)
        return None


async def delete_lesson(code):
    try:
        deleted = await repository.delete_lesson(code)
        if deleted == 0:
            logger.exception(f"Урок '{code}' не найден.")
            return None
        return True
    except Exception as e:
        logger.exception("Ошибка в delete_lesson:", e)
        return None


async def get_upcoming_user_lessons(tg_id):
    try:
        user_surfs = await repository.get_upcoming_user_lessons(tg_id)
        if not user_surfs:
            return None

        result = []
        for us in user_surfs:
            payment = await repository.get_user_lesson_payment(us.user.user_id, us.surf.surf_id)
            result.append(serialize_lesson(surf=us.surf, payment=payment))
        return result

    except Exception as e:
        logger.exception("Ошибка в get_upcoming_user_lessons:", e)
        return None


# --------------------
# TOUR
# --------------------
async def create_tour(tour_name, tour_desc, tour_places, start_date, start_time, end_date, tour_price,
                      tour_destination):
    try:
        destination = await repository.get_destination_by_name(tour_destination)
        if destination is None:
            return False
        await repository.create_tour(
            Tour(
                tour_name=tour_name,
                tour_desc=tour_desc,
                tour_places=tour_places,
                start_date=start_date.date().strftime("%d.%m.%Y"),
                start_time=start_time,
                end_date=end_date.date().strftime("%d.%m.%Y"),
                tour_price=tour_price,
                tour_destination=destination,
            )
        )
        return True
    except Exception as e:
        logger.exception("Ошибка в create_tour:", e)
        return None


async def get_tour_by_name(tour_name):
    try:
        t = await repository.get_tour_by_name(tour_name)
        if not t:
            return None
        return serialize_tour(t)
    except Exception as e:
        logger.exception("Ошибка в get_tour_by_name:", e)
        return None


async def get_future_paid_tour(name):
    return await repository.get_future_paid_tour(name)

async def get_all_tours_with_places():
    try:
        tours = await repository.get_all_tours_with_places()
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]
    except Exception as e:
        logger.exception("Ошибка в get_all_tours_with_places:", e)
        return None


async def reduce_places_on_tour(tour_name, count):
    try:
        result = await repository.reduce_places_on_tour(tour_name, count)
        if result is None:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        if not result:
            logger.exception(f"Нельзя уменьшить места: недостаточно свободных мест в '{tour_name}'.")
            return False
        return True
    except Exception as e:
        logger.exception("Ошибка в reduce_places_on_tour:", e)
        return None


async def add_places_on_tour(tour_name, count):
    try:
        result = await repository.add_places_on_tour(tour_name, count)
        if result is None:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        return True
    except Exception as e:
        logger.exception("Ошибка в add_places_on_tour:", e)
        return None


async def delete_tour(tour_name):
    try:
        deleted = await repository.delete_tour(tour_name)
        if deleted == 0:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        return True
    except Exception as e:
        logger.exception("Ошибка в delete_tour:", e)
        return None


async def get_all_booked_tours():
    try:
        tours = await repository.get_all_booked_tours()
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]
    except Exception as e:
        logger.exception("Ошибка в get_all_booked_tours:", e)
        return None


async def get_all_tours():
    try:
        tours = await repository.get_all_tours()
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]
    except Exception as e:
        logger.exception("Ошибка в get_all_tours:", e)
        return None


async def get_all_tour_by_dest(destination_name):
    try:
        tours = await repository.get_all_tour_by_dest(destination_name)
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]
    except Exception as e:
        logger.exception("Ошибка в get_all_tour_by_dest:", e)
        return None


# --------------------
# DESTINATION
# --------------------
async def create_destination(name):
    try:
        dest = await repository.get_destination_by_name(name)
        if dest is None:
            await repository.create_destination(
                Destination(destination=name)
            )
            return True
        else:
            return False
    except Exception as e:
        logger.exception("Ошибка в create_destination:", e)
        return None


async def get_destination_by_name(name):
    try:
        d = await repository.get_destination_by_name(name)
        if not d:
            return None
        return serialize_destination(d)
    except Exception as e:
        logger.exception("Ошибка в get_destination_by_name:", e)
        return None


async def get_all_destinations():
    try:
        dest = await repository.get_all_destinations()
        if not dest:
            return None
        return [serialize_destination(dest=d) for d in dest]
    except Exception as e:
        logger.exception("Ошибка в get_all_destinations:", e)
        return None


async def delete_destination_by_name(name):
    try:
        await repository.delete_destination_by_name(name)
        return True
    except Exception as e:
        logger.exception("Ошибка в delete_destination_by_name:", e)
        return None


# --------------------
# PAYMENTS
# --------------------
async def create_tour_payment(tg_id, price, tour_name):
    try:
        user = await repository.get_user_by_tg_id(tg_id)
        tour = await repository.get_tour_by_name(tour_name)

        if not user or not tour:
            # Не нашли пользователя или урок
            return None

        # Пробуем создать UserTour
        await repository.create_user_tour(user, tour)

        # Создаём оплату
        payment = await repository.create_tour_payment(
            TourPayment(
                pay_date=datetime.datetime.now().strftime("%d.%m.%Y"),
                pay_price=price,
                user=user,
                tour=tour
            )
        )

        return payment

    except Exception as e:
        logger.exception("Ошибка в create_surf_payment:", e)
        return None


async def create_surf_payment(tg_id, price, code):
    try:
        user = await repository.get_user_by_tg_id(tg_id)
        surf = await repository.get_lesson_by_code(code)

        if not user or not surf:
            # Не нашли пользователя или урок
            return None

        # Пробуем создать UserSurf
        await repository.create_user_surf(user, surf)

        # Создаём оплату
        payment = await repository.create_surf_payment(
            SurfPayment(
                pay_date=datetime.datetime.now().strftime("%d.%m.%Y"),
                pay_price=price,
                user=user,
                surf=surf
            )
        )

        return payment

    except Exception as e:
        logger.exception("Ошибка в create_surf_payment:", e)
        return None


async def get_lesson_types():
    try:
        types = await repository.get_lesson_types()
        if types is None: return None
        return types
    except Exception as e:
        logger.exception(e)


async def add_lesson_type(type_lesson):
    try:
        await repository.add_lesson_type(type_lesson)
        return True
    except Exception as e:
        logger.exception(e)


async def has_future_bookings_for_destination(destination) -> bool | None:
    try:
        has_booked = await repository.has_future_bookings_for_destination(destination)
        return has_booked
    except Exception as e:
        logger.exception(e)
