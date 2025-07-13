import logging

from database.models import TourPayment, SurfPayment

logger = logging.getLogger(__name__)


class PaymentRepository:

    async def create_tour_payment(self, payment: TourPayment) -> TourPayment:
        return await TourPayment.create(
            pay_date=payment.pay_date,
            pay_price=payment.pay_price,
            user=payment.user,
            tour=payment.tour
        )

    async def create_surf_payment(self, payment: SurfPayment) -> SurfPayment:
        return await SurfPayment.create(
            pay_date=payment.pay_date,
            pay_price=payment.pay_price,
            user=payment.user,
            surf=payment.surf
        )

    async def get_user_tour_payment(self, user_id, tour_id) -> TourPayment:
        return await TourPayment.filter(
            user_id=user_id,
            tour_id=tour_id
        ).first()
