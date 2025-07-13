from repository.booking_repository import BookingRepository


class BookingService:
    def __init__(self, booking_repo: BookingRepository):
        self.repo = booking_repo

    async def has_future_bookings_for_destination(self, destination) -> bool | None:
        """
            Проверяет есть ли будущие бронирования для указанного направления.

            Args:
                destination: Название направления (case-sensitive)

            Returns:
                bool: True если есть хотя бы одна активная бронь,
                      False если броней нет или направление не существует

            Raises:
                DatabaseError: При ошибках запроса к БД
            """
        has_booked = await self.repo.has_future_bookings_for_destination(destination)
        return has_booked
