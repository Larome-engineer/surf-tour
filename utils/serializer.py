from typing import Any

from database.models import SurfLesson, User, Tour, TourPayment, SurfPayment, Destination, UserSurf


def serialize_user(user: User | UserSurf) -> dict:
    return {
        "id": user.user_id,
        "tg_id": user.user_tg_id,
        "name": user.user_name,
        "email": user.user_email,
        "phone": user.user_phone
    }

def serialize_tour(tour: Tour, payment: TourPayment = None) -> dict:
    d = {
        "name": tour.tour_name,
        "desc": tour.tour_desc,
        "dest": tour.tour_destination.destination if tour.tour_destination else None,
        "places": tour.tour_places,
        "price": tour.tour_price,
        "start_date": tour.start_date,
        "time": tour.start_time,
        "end_date": tour.end_date,
    }
    if payment is not None:
        d['paid'] = payment.pay_price if payment else 0.0

    return d


def serialize_lesson(surf: SurfLesson, payment: SurfPayment = None, users: list[User] = None) -> dict:
    d = {
        "unicode": surf.unique_code,
        "dest": surf.surf_destination.destination if surf.surf_destination else None,
        "places": surf.surf_places,
        "start_date": surf.start_date,
        "price": surf.surf_price,
        "time": surf.start_time,
        "duration": surf.surf_duration,
        "type": surf.surf_type.type,
        "desc": surf.surf_desc,
    }

    if payment is not None:
        d['paid'] = payment.pay_price if payment else 0.0
    if users is not None:
        d['users'] = users
    return d

def serialize_destination(dest: Destination) -> dict:
    return {
        "id": dest.dest_id,
        "name": dest.destination
    }