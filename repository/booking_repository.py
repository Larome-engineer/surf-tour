import logging
from datetime import datetime

from database.models import Destination, Tour, UserTour, UserSurf, SurfLesson

logger = logging.getLogger(__name__)


class BookingRepository:
    async def has_future_bookings_for_destination(self, dest_name: str) -> bool:
        try:
            destination = await Destination.get_or_none(destination=dest_name.lower())
            if not destination:
                return False  # Если направления нет — точно ничего нет

            today = datetime.today().date()

            # Проверка туров
            tours = await Tour.filter(
                tour_destination=destination
            ).only("tour_id", "start_date").all()

            for tour in tours:
                if tour.start_date >= today:
                    # Проверяем есть ли записи
                    if await UserTour.filter(tour=tour).exists():
                        return True

            # Проверка уроков
            lessons = await SurfLesson.filter(
                surf_destination=destination
            ).only("surf_id", "start_date").all()

            for lesson in lessons:
                if lesson.start_date >= today:
                    if await UserSurf.filter(surf=lesson).exists():
                        return True

            return False
        except Exception as e:
            logger.error(f"Failed to has_future_bookings_for_destination: {str(e)}")
            raise
