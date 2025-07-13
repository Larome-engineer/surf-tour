import logging
from datetime import datetime

from database.models import TourPayment, SurfPayment
from repository.payment_repository import PaymentRepository
from service.lesson_service import LessonService
from service.tour_service import TourService
from service.user_service import UserService

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self,
                 payment_repo: PaymentRepository,
                 user_service: UserService,
                 tour_service: TourService,
                 lesson_service: LessonService):
        self.repo = payment_repo
        self.user_service = user_service
        self.tour_service = tour_service
        self.lesson_service = lesson_service

    async def create_tour_payment(self, tg_id, price, tour_name):
        user = await self.user_service.get_user(tg_id)
        tour = await self.tour_service.get_tour_by_name(tour_name)

        if not user or not tour:
            # Не нашли пользователя или урок
            return None

        # Пробуем создать UserTour
        await self.tour_service.create_user_tour(user, tour)

        # Создаём оплату
        payment = await self.repo.create_tour_payment(
            TourPayment(
                pay_date=datetime.now().strftime("%d.%m.%Y"),
                pay_price=price,
                user=user,
                tour=tour
            )
        )

        return payment

    async def create_surf_payment(self, tg_id, price, code):
        user = await self.user_service.get_user(tg_id)
        surf = await self.lesson_service.get_lesson(code)

        if not user or not surf:
            # Не нашли пользователя или урок
            return None

        # Пробуем создать UserSurf
        await self.lesson_service.create_user_surf(user, surf)

        # Создаём оплату
        payment = await self.repo.create_surf_payment(
            SurfPayment(
                pay_date=datetime.now().strftime("%d.%m.%Y"),
                pay_price=price,
                user=user,
                surf=surf
            )
        )

        return payment
