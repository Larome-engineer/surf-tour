import logging
from datetime import date
from typing import Optional

from database.models import Tour, UserTour
from database.models import TourPayment
from utils.date_utils import parse_date

logger = logging.getLogger(__name__)


class TourRepository:

    async def create_tour(self, tour: Tour) -> Tour:
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

    async def get_all_tour_by_dest(self, destination_name) -> list[Tour]:
        return await Tour.filter(
            tour_destination__destination=destination_name
        ).prefetch_related("tour_destination")

    async def get_tour_by_name(self, tour_name) -> Optional[Tour]:
        return await Tour.filter(tour_name=tour_name).prefetch_related("tour_destination").first()

    async def get_all_tours(self) -> list[Tour]:
        return await Tour.all().prefetch_related("tour_destination")

    async def get_all_tours_with_places(self) -> list[Tour]:
        return await Tour.filter(tour_places__gt=0).prefetch_related("tour_destination")

    async def get_future_paid_tour(self, name) -> Tour | None:
        tour = await self.get_tour_by_name(name)
        if not tour:
            return None
        try:
            start = parse_date(tour.start_date)
        except Exception:
            return None
        if start < date.today() or not await TourPayment.filter(tour=tour).exists():
            return None
        return tour

    async def reduce_places_on_tour(self, tour_name, count) -> bool | None:
        tour = await self.get_tour_by_name(tour_name)
        if not tour:
            return None
        if tour.tour_places < count:
            return False
        tour.tour_places -= count
        await tour.save()
        return True

    async def add_places_on_tour(self, tour_name, count) -> bool | None:
        tour = await self.get_tour_by_name(tour_name)
        if not tour:
            return None
        tour.tour_places += count
        await tour.save()
        return True

    async def delete_tour(self, tour_name) -> bool:
        deleted = await Tour.filter(tour_name=tour_name).delete()
        return deleted > 0

    async def get_all_booked_tours(self) -> list[Tour]:
        return await Tour.filter(user_tours__isnull=False).distinct().prefetch_related("tour_destination")

    async def get_upcoming_user_tours(self, tg_id) -> list[UserTour]:
        all_tours = await UserTour.filter(
            user__user_tg_id=tg_id
        ).prefetch_related("tour__tour_destination")
        today = date.today()
        return [
            ut for ut in all_tours
            if parse_date(ut.tour.start_date) >= today
        ]

    async def get_user_tour_details(self, tg_id, tour_name) -> UserTour:
        return await UserTour.filter(
            user__user_tg_id=tg_id,
            tour__tour_name=tour_name
        ).prefetch_related(
            "tour",
            "tour__tour_destination"
        ).first()

    async def get_user_tour_payment(self, user_id, tour_id) -> TourPayment:
        return await TourPayment.filter(
            user_id=user_id,
            tour_id=tour_id
        ).first()

    async def create_user_tour(self, user, tour) -> bool:
        exists = await UserTour.filter(user=user, tour=tour).exists()
        if exists:
            return False
        await UserTour.create(user=user, tour=tour)
        return True
