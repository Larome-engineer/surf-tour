from dependency_injector import containers, providers

from repository.booking_repository import BookingRepository
from repository.destination_repository import DestRepository
from repository.lesson_repository import LessonRepository
from repository.payment_repository import PaymentRepository
from repository.tour_repository import TourRepository
from repository.user_repository import UserRepository
from service.booking_service import BookingService
from service.destination_service import DestService
from service.lesson_service import LessonService
from service.payment_service import PaymentService
from service.tour_service import TourService
from service.user_service import UserService


class Container(containers.DeclarativeContainer):
    lesson_repo = providers.Factory(LessonRepository)
    booking_repo = providers.Factory(BookingRepository)
    dest_repo = providers.Factory(DestRepository)
    payment_repo = providers.Factory(PaymentRepository)
    tour_repo = providers.Factory(TourRepository)
    user_repo = providers.Factory(UserRepository)

    user_service = providers.Factory(
        UserService,
        user_repo=user_repo
    )
    destination_service = providers.Factory(
        DestService,
        dest_repo=dest_repo
    )

    booking_service = providers.Factory(
        BookingService,
        booking_repo=booking_repo
    )
    lesson_service = providers.Factory(
        LessonService,
        lesson_repo=lesson_repo, destination_service=destination_service
    )
    tour_service = providers.Factory(
        TourService,
        tour_repo=tour_repo, destination_service=destination_service
    )
    payment_service = providers.Factory(
        PaymentService,
        payment_repo=payment_repo,
        user_service=user_service,
        tour_service=tour_service,
        lesson_service=lesson_service
    )


