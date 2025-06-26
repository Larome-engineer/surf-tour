from .models import *

from datetime import date


# Добавить направление
async def create_destination(destination: str):
    await Destination.create(destination=destination)


# Добавить тур
async def create_tour(name, desc, places, start, end, price, destination):
    await Tour.create(
        tour_name=name,
        tour_desc=desc,
        tour_places=places,
        start_date=start,
        end_date=end,
        tour_price=price,
        tour_destination=await Destination.get(destination=destination)
    )


# Создать пользователя
async def create_user(tg_id, username, email, phone):
    await User.create(
        user_tg_id=tg_id,
        user_name=username,
        user_email=email,
        user_phone=phone
    )

async def update_user(tg_id, username, email, phone):
    user = await User.get_or_none(user_tg_id=tg_id)
    user.user_name = username
    user.user_email = email
    user.user_phone = phone
    await user.save()

# Создать платеж
async def create_payment(date, price, user, tour):
    await Payment.create(
        pay_date=date,
        pay_price=price,
        user=user,
        tour=tour
    )


async def add_user_tour(user, tour, places):
    ut = await UsersTours.get_or_none(user=user, tour=tour)
    if ut:
        ut.ur_places += places
        await ut.save()
    else:
        await UsersTours.create(user=user, tour=tour, ur_places=places)


from datetime import date


from datetime import date

from collections import defaultdict
from datetime import date

async def get_user_tour_details(user_tg_id: int, tour_name: str):
    user = await User.get_or_none(user_tg_id=user_tg_id).prefetch_related(
        "tours__tour__tour_destination",
        "payments__tour"
    )
    if not user:
        return None

    # Словарь: tour_id → сумма всех оплат
    payments_by_tour = defaultdict(float)
    for payment in user.payments:
        payments_by_tour[payment.tour.tour_id] += float(payment.pay_price)

    for ut in user.tours:
        tour = ut.tour
        if tour.tour_name == tour_name and tour.start_date > date.today():
            return {
                "tour_name": tour.tour_name,
                "destination": tour.tour_destination.destination,
                "description": tour.tour_desc,
                "start_date": tour.start_date.strftime("%d.%m.%Y"),
                "end_date": tour.end_date.strftime("%d.%m.%Y"),
                "places": ut.ur_places,
                "price_paid": payments_by_tour[tour.tour_id]
            }

    return None




async def get_upcoming_user_tours(user_tg_id: int):
    user = await User.get_or_none(user_tg_id=user_tg_id).prefetch_related(
        "tours__tour__tour_destination",
        "payments__tour"
    )
    if not user:
        return None

    # Словарь: tour_id → сумма оплаты
    payments_by_tour = {
        payment.tour: payment.pay_price
        for payment in user.payments
    }

    result = []
    for ut in user.tours:
        tour = ut.tour
        if tour.start_date > date.today():
            result.append({
                "tour_name": tour.tour_name,
                "destination": tour.tour_destination.destination,
                "start_date": tour.start_date.strftime("%d.%m.%Y"),
                "end_date": tour.end_date.strftime("%d.%m.%Y"),
                "places": ut.ur_places,
                "price_paid": float(payments_by_tour.get(tour.tour_id, 0))
            })

    return result if result else None


# Получить список доступных направлений
async def get_all_dest():
    return await Destination.all().values_list("destination", flat=True)


async def get_all_tours():
    return await Tour.all().prefetch_related("tour_destination")


async def get_all_tours_with_places():
    return await Tour.filter(tour_places__gt=0).prefetch_related("tour_destination")


async def get_tour_names():
    return await Tour.all().prefetch_related("tour_destination")


async def get_tour_by_name(tour_name):
    return await Tour.get_or_none(tour_name=tour_name).prefetch_related("tour_destination")


# Получить список туров по направлению
async def get_all_tour_by_dest(destination_name):
    destination = await Destination.get(destination=destination_name)
    return await Tour.filter(tour_destination=destination).prefetch_related("tour_destination")


async def get_all_user_tours(user_tg_id):
    user = await User.get_or_none(user_tg_id=user_tg_id).prefetch_related("payments__tour")
    if not user:
        return None

    return [payment.tour for payment in user.payments]


async def get_user(tg_id):
    return await User.get(user_tg_id=tg_id)


async def get_tour(tour_name):
    return await Tour.get(tour_name=tour_name)


# Получить список свободных туров по направлению
async def get_all_free_tour_by_dest(destination_name):
    destination = await Destination.get(destination=destination_name)
    return await Tour.filter(
        tour_destination=destination,
        tour_places__gt=0  # gt = greater than
    ).order_by("start_date")


# Получить информацию пользователя по телефону
async def get_user_by_phone(phone: str):
    return await User.get_or_none(user_phone=phone).prefetch_related("tours__tour")


# Получить информацию пользователя по Email
async def get_user_by_email(email: str):
    return await User.get_or_none(user_email=email).prefetch_related("tours__tour")


async def get_user_by_tg_id(tg_id):
    return await User.get_or_none(user_tg_id=tg_id).prefetch_related("tours__tour")


# Получить список пользователей на конкретный тур
async def get_users_by_tour(tour_name: str):
    tour = await Tour.get(tour_name=tour_name)
    users_tours = await UsersTours.filter(tour=tour).prefetch_related("user")
    return [ut.user for ut in users_tours]


# Получить список всех пользователей
async def get_all_users():
    return await User.all().values_list("user_tg_id", "user_name", "user_email", "user_phone")


async def get_all_users_ids() -> list[int]:
    return await User.all().values_list("user_tg_id", flat=True)


# Получить список всех оплаченных туров
async def get_all_booked_tours():
    return await Payment.all().prefetch_related("tour", "user")


# Получить кол-во мест на тур
async def get_places_by_tour(tour_name):
    tour = await Tour.get(tour_name=tour_name)
    return tour.tour_places


# Получить тур по дате начала
async def get_tours_by_start_date(date):
    return await Tour.filter(start_date=date).order_by("tour_name")


# Получить тур в диапазоне дат
async def get_tours_by_dates_between(date_1, date_2):
    return await Tour.filter(start_date__gte=date_1, end_date__lte=date_2).order_by("start_date")


# Добавить мест на тур
async def add_places_on_tour(tour_name, num_of_places: int):
    tour = await Tour.get(tour_name=tour_name)
    tour.tour_places += num_of_places
    await tour.save()


async def reduce_places_on_tour(tour_name, num_of_places: int):
    tour = await Tour.get(tour_name=tour_name)
    tour.tour_places -= num_of_places
    await tour.save()


# Удалить тур
async def delete_tour(tour_name: str):
    await Tour.filter(tour_name=tour_name).delete()


# Удалить направление
async def delete_dest(dest_name: str):
    await Destination.filter(destination=dest_name).delete()
