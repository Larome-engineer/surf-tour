import uuid
from datetime import datetime, date
from typing import Optional

from tortoise.expressions import Q

from utils.date_utils import parse_date
from .models import *


# ----------------
# USER REPOSITORY
# ----------------
async def create_user(user: User) -> User:
    return await User.create(
        user_tg_id=user.user_tg_id,
        user_name=user.user_name,
        user_email=user.user_email,
        user_phone=user.user_phone
    )


async def get_all_users() -> list[User]:
    return await User.all()


async def get_user_by_tg_id(tg_id) -> Optional[User]:
    user = await User.filter(user_tg_id=tg_id).prefetch_related(
        "tours__tour",
        "surfs__surf",
        "tour_payments__tour",
        "surf_payments__surf"
    ).first()
    return user


async def update_user(user_updated: User) -> bool:
    user = await User.get_or_none(user_tg_id=user_updated.user_tg_id)
    if user is not None:
        if user_updated.user_name is not None:
            user.user_name = user_updated.user_name
        if user_updated.user_email is not None:
            user.user_email = user_updated.user_email
        if user_updated.user_phone is not None:
            user.user_phone = user_updated.user_phone
        await user.save()
        return True
    else:
        return False


async def get_user_by_phone_or_email(phone_or_email) -> Optional[User]:
    return await User.filter(
        Q(user_phone=phone_or_email) | Q(user_email=phone_or_email)
    ).first()


async def delete_user_by_tg_id(tg_id) -> Optional[User]:
    await User.filter(user_tg_id=tg_id).delete()


async def get_all_users_ids() -> list[str]:
    return await User.all().values_list("user_tg_id", flat=True)


# --------------------
# LESSON REPOSITORY
# --------------------
async def get_lesson_types() -> list[LessonType]:
    return await LessonType.all()


async def get_lesson_type(lesson_type) -> LessonType:
    return await LessonType.get_or_none(type=lesson_type)


async def create_lesson(surf_lesson: SurfLesson) -> str:
    code = str(uuid.uuid4())
    await SurfLesson.create(
        unique_code=code,
        surf_desc=surf_lesson.surf_desc,
        surf_places=surf_lesson.surf_places,
        start_date=surf_lesson.start_date,
        start_time=surf_lesson.start_time,
        surf_duration=surf_lesson.surf_duration,
        surf_price=surf_lesson.surf_price,
        surf_destination=surf_lesson.surf_destination,
        surf_type=surf_lesson.surf_type
    )
    return code


async def get_all_lessons() -> list[SurfLesson]:
    return await SurfLesson.all().prefetch_related("surf_destination", "surf_type")


async def get_all_lessons_with_places() -> list[SurfLesson]:
    return await SurfLesson.filter(surf_places__gt=0).prefetch_related("surf_destination", "surf_type")


async def get_lessons_by_date(start_date) -> list[SurfLesson]:
    return await SurfLesson.filter(start_date=start_date).prefetch_related("surf_destination", "surf_type")


async def get_lesson_by_code(code) -> Optional[SurfLesson]:
    return await SurfLesson.filter(unique_code=code).prefetch_related("surf_destination", "surf_type").first()


async def get_future_lessons() -> list[SurfLesson]:
    lessons = await SurfLesson.all().prefetch_related("surf_destination", "surf_type")
    today = date.today()
    return [
        l for l in lessons
        if parse_date(l.start_date) >= today
    ]


async def get_all_paid_lesson() -> list[SurfLesson]:
    return await SurfLesson.filter(payments__isnull=False).distinct().all().prefetch_related("surf_destination",
                                                                                             "surf_type")


async def get_all_booked_lessons_future() -> list[SurfLesson]:
    all_lessons = await SurfLesson.filter(user_surfs__isnull=False).distinct().prefetch_related(
        "surf_destination", "user_surfs__user", "surf_type"
    )
    today = date.today()
    result = []
    for l in all_lessons:
        try:
            dt = parse_date(l.start_date)
            if dt >= today:
                result.append(l)
        except ValueError:
            continue
    return result


async def get_all_lessons_by_dest(destination_name) -> list[SurfLesson]:
    all_lessons = await SurfLesson.filter(
        surf_destination__destination=destination_name
    ).prefetch_related("surf_destination", "surf_type")
    today = date.today()
    return [
        l for l in all_lessons
        if parse_date(l.start_date) >= today
    ]


async def get_all_booked_lessons() -> list[SurfLesson]:
    return await SurfLesson.filter(
        user_surfs__isnull=False
    ).distinct().prefetch_related(
        "surf_destination",
        "user_surfs__user",
        "surf_type"
    )


async def reduce_places_on_lesson(code, count) -> bool | None:
    lesson = await get_lesson_by_code(code)
    if not lesson:
        return None
    if lesson.surf_places < count:
        return False
    lesson.surf_places -= count
    await lesson.save()
    return True


async def add_places_on_lesson(code, count) -> bool | None:
    lesson = await get_lesson_by_code(code)
    if not lesson:
        return None
    lesson.surf_places += count
    await lesson.save()
    return True


async def delete_lesson(code) -> bool:
    deleted = await SurfLesson.filter(unique_code=code).delete()
    return deleted > 0


async def get_upcoming_user_lessons(tg_id) -> list[UserSurf]:
    all_surfs = await UserSurf.filter(
        user__user_tg_id=tg_id
    ).prefetch_related("surf__surf_destination", "surf__surf_type")
    today = date.today()
    result = []
    for us in all_surfs:
        try:
            d = parse_date(us.surf.start_date)
            if d >= today:
                result.append(us)
        except ValueError:
            continue
    return result


async def get_user_lesson_details(tg_id, code) -> UserSurf:
    return await UserSurf.filter(
        user__user_tg_id=tg_id,
        surf__unique_code=code
    ).prefetch_related("surf__surf_destination", "surf__surf_type").first()


async def get_user_lesson_payment(user_id, surf_id) -> SurfPayment:
    return await SurfPayment.filter(
        user_id=user_id,
        surf_id=surf_id
    ).first()


async def get_future_paid_lesson(code) -> SurfLesson | None:
    lesson = await get_lesson_by_code(code)
    if not lesson:
        return None
    try:
        start = parse_date(lesson.start_date)
    except Exception:
        return None
    if start < date.today() or not await SurfPayment.filter(surf=lesson).exists():
        return None
    return lesson


# --------------------
# TOUR REPOSITORY
# --------------------
async def create_tour(tour: Tour) -> Tour:
    return await Tour.create(
        tour_name=tour.tour_name,
        tour_desc=tour.tour_desc,
        tour_places=tour.tour_places,
        start_date=tour.start_date,
        start_time=tour.start_time,
        end_date=tour.end_date,
        tour_price=tour.tour_price,
        tour_destination=tour.tour_destination
    )


async def get_all_tour_by_dest(destination_name) -> list[Tour]:
    return await Tour.filter(
        tour_destination__destination=destination_name
    ).prefetch_related("tour_destination")


async def get_tour_by_name(tour_name) -> Optional[Tour]:
    return await Tour.filter(tour_name=tour_name).prefetch_related("tour_destination").first()


async def get_all_tours() -> list[Tour]:
    return await Tour.all().prefetch_related("tour_destination")


async def get_all_tours_with_places() -> list[Tour]:
    return await Tour.filter(tour_places__gt=0).prefetch_related("tour_destination")


async def get_future_paid_tour(name) -> Tour | None:
    tour = await get_tour_by_name(name)
    if not tour:
        return None
    try:
        start = parse_date(tour.start_date)
    except Exception:
        return None
    if start < date.today() or not await TourPayment.filter(tour=tour).exists():
        return None
    return tour


async def reduce_places_on_tour(tour_name, count) -> bool | None:
    tour = await get_tour_by_name(tour_name)
    if not tour:
        return None
    if tour.tour_places < count:
        return False
    tour.tour_places -= count
    await tour.save()
    return True


async def add_places_on_tour(tour_name, count) -> bool | None:
    tour = await get_tour_by_name(tour_name)
    if not tour:
        return None
    tour.tour_places += count
    await tour.save()
    return True


async def delete_tour(tour_name) -> bool:
    deleted = await Tour.filter(tour_name=tour_name).delete()
    return deleted > 0


async def get_all_booked_tours() -> list[Tour]:
    return await Tour.filter(user_tours__isnull=False).distinct().prefetch_related("tour_destination")


async def get_upcoming_user_tours(tg_id) -> list[UserTour]:
    all_tours = await UserTour.filter(
        user__user_tg_id=tg_id
    ).prefetch_related("tour__tour_destination")
    today = date.today()
    return [
        ut for ut in all_tours
        if parse_date(ut.tour.start_date) >= today
    ]


async def get_user_tour_details(tg_id, tour_name) -> UserTour:
    return await UserTour.filter(
        user__user_tg_id=tg_id,
        tour__tour_name=tour_name
    ).prefetch_related(
        "tour",
        "tour__tour_destination"
    ).first()


async def get_user_tour_payment(user_id, tour_id) -> TourPayment:
    return await TourPayment.filter(
        user_id=user_id,
        tour_id=tour_id
    ).first()


# --------------------
# DESTINATION REPOSITORY
# --------------------
async def create_destination(destination: Destination) -> Destination:
    return await Destination.create(
        destination=destination.destination
    )


async def get_destination_by_name(name) -> Destination:
    return await Destination.get_or_none(destination=name)


async def get_all_destinations() -> list[Destination]:
    return await Destination.all()


async def delete_destination_by_name(name) -> bool:
    deleted = await Destination.filter(destination=name).delete()
    return deleted > 0


# --------------------
# PAYMENT REPOSITORY
# --------------------
async def create_tour_payment(payment: TourPayment) -> TourPayment:
    return await TourPayment.create(
        pay_date=payment.pay_date,
        pay_price=payment.pay_price,
        user=payment.user,
        tour=payment.tour
    )


async def create_surf_payment(payment: SurfPayment) -> SurfPayment:
    return await SurfPayment.create(
        pay_date=payment.pay_date,
        pay_price=payment.pay_price,
        user=payment.user,
        surf=payment.surf
    )


# --------------------
# USER|SURF_TOUR REPOSITORY
# --------------------
async def create_user_tour(user, tour) -> bool:
    exists = await UserTour.filter(user=user, tour=tour).exists()
    if exists:
        return False
    await UserTour.create(user=user, tour=tour)
    return True


async def create_user_surf(user, surf) -> bool:
    exists = await UserSurf.filter(user=user, surf=surf).exists()
    if exists:
        return False
    await UserSurf.create(user=user, surf=surf)
    return True


# --------------------
# TYPE REPOSITORY
# --------------------
async def add_lesson_type(type_lesson) -> LessonType:
    return await LessonType.create(
        type=type_lesson
    )


# --------------------
# ADDITIONAL UTIL REPOSITORY
# --------------------
async def has_future_bookings_for_destination(dest_name: str) -> bool:
    """
    Проверяет, есть ли предстоящие туры или уроки с хотя бы одной записью пользователя.
    """
    destination = await Destination.get_or_none(destination=dest_name)
    if not destination:
        return False  # Если направления нет — точно ничего нет

    today = datetime.today().date()

    # Проверка туров
    tours = await Tour.filter(
        tour_destination=destination
    ).only("tour_id", "start_date").all()

    for tour in tours:
        try:
            start_date = parse_date(tour.start_date)
        except ValueError:
            continue  # Если дата кривая — пропускаем
        if start_date >= today:
            # Проверяем есть ли записи
            if await UserTour.filter(tour=tour).exists():
                return True

    # Проверка уроков
    lessons = await SurfLesson.filter(
        surf_destination=destination
    ).only("surf_id", "start_date").all()

    for lesson in lessons:
        try:
            start_date = parse_date(lesson.start_date)
        except ValueError:
            continue
        if start_date >= today:
            if await UserSurf.filter(surf=lesson).exists():
                return True

    return False
