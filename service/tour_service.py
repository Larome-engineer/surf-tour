import logging
from datetime import datetime

from database.models import Tour
from repository.tour_repository import TourRepository
from service.destination_service import DestService
from utils.serializer import serialize_tour

logger = logging.getLogger(__name__)


class TourService:
    def __init__(self, tour_repo: TourRepository, destination_service: DestService):
        self.repo = tour_repo
        self.dest_service = destination_service

    async def create_tour(self,
                          tour_name: str,
                          tour_desc: str,
                          tour_places: int,
                          start_date: datetime,
                          start_time: str,
                          end_date: datetime,
                          tour_price: int,
                          tour_destination: str
                          ):
        destination = await self.dest_service.get_destination(tour_destination.lower())
        if destination is None:
            return False

        await self.repo.create_tour(
            Tour(
                tour_name=tour_name,
                tour_desc=tour_desc,
                tour_places=tour_places,
                start_date=start_date.date(),
                start_time=start_time,
                end_date=end_date.date(),
                tour_price=tour_price,
                tour_destination=destination,
            )
        )
        return True

    async def get_tour_by_name(self, tour_name):
        t = await self.repo.get_tour_by_name(tour_name)
        if not t:
            return None
        return serialize_tour(t)

    async def get_tour(self, tour_name):
        t = await self.repo.get_tour_by_name(tour_name)
        if not t:
            return None
        return t

    async def get_future_paid_tour(self, name):
        return await self.repo.get_future_paid_tour(name)

    async def get_all_tours_with_places(self):
        tours = await self.repo.get_all_tours_with_places()
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]

    async def reduce_places_on_tour(self, tour_name, count):
        result = await self.repo.reduce_places_on_tour(tour_name, count)
        if result is None:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        if not result:
            logger.exception(f"Нельзя уменьшить места: недостаточно свободных мест в '{tour_name}'.")
            return False
        return True

    async def add_places_on_tour(self, tour_name, count):
        result = await self.repo.add_places_on_tour(tour_name, count)
        if result is None:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        return True

    async def delete_tour(self, tour_name):
        deleted = await self.repo.delete_tour(tour_name)
        if deleted == 0:
            logger.exception(f"Тур '{tour_name}' не найден.")
            return None
        return True

    async def get_all_booked_tours(self):
        tours = await self.repo.get_all_booked_tours()
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]

    # async def get_all_tours(self):
    #     tours = await self.repo.get_all_tours()
    #     if not tours:
    #         return None
    #     return [serialize_tour(tour=t) for t in tours]

    async def get_all_tour_by_dest(self, destination_name: str):
        tours = await self.repo.get_all_tour_by_dest(destination_name.lower())
        if not tours:
            return None
        return [serialize_tour(tour=t) for t in tours]

    async def get_upcoming_user_tours(self, tg_id):
        user_tours = await self.repo.get_upcoming_user_tours(tg_id)
        if not user_tours:
            return None

        result = []
        for ut in user_tours:
            payment = await self.repo.get_user_tour_payment(ut.user_id, ut.tour_id)
            result.append(serialize_tour(ut.tour, payment))
        return result

    async def get_user_tour_details(self, tg_id, tour_name):
        ut = await self.repo.get_user_tour_details(tg_id, tour_name)
        if not ut:
            return None

        payment = await self.repo.get_user_tour_payment(ut.user_id, ut.tour_id)
        return serialize_tour(ut.tour, payment)

    async def create_user_tour(self, user, tour):
        created = await self.repo.create_user_tour(user, tour)
        return created
