from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import PreCheckoutQuery, SuccessfulPayment, BufferedInputFile
from dependency_injector.wiring import Provide, inject

from bot.config import NOTIFICATION_CHAT
from bot.create import payment_payload, surf_bot
from DIcontainer import Container
from bot.handlers.handler_utils import safe_send_document, safe_send
from bot.keyboards.user import user_main_menu
from service.lesson_service import LessonService
from service.payment_service import PaymentService
from service.tour_service import TourService
from service.user_service import UserService
from utils.generate_pdf import generate_invoice_pdf_lesson, generate_invoice_pdf_tour

payment = Router()


@payment.pre_checkout_query()
@inject
async def process_pre_checkout(
        event: PreCheckoutQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service],
        tour_service: TourService = Provide[Container.tour_service]
):
    payload = event.invoice_payload
    if payload == "event: ApplyUserLessonBooking":
        lesson = await lesson_service.get_lesson_by_code(
            payment_payload[event.from_user.id]['lesson']['unicode']
        )
        if not lesson or int(lesson['places']) <= 0:
            payment_payload.pop(event.from_user.id)
            await state.clear()
            await event.answer(
                ok=False,
                error_message="❌ <b>Места закончились...\n• Этот урок больше недоступен.</b>",
            )
            await surf_bot.delete_message(
                chat_id=event.from_user.id,
                message_id=event.id,
            )
            return
        payment_payload[event.from_user.id]['lesson']['lesson'] = lesson
        await event.answer(ok=True)

    elif payload == "event: ApplyUserTourBooking":
        tour = await tour_service.get_tour_by_name(
            payment_payload[event.from_user.id]['tour']['tour_name']
        )

        if not tour or int(tour['places']) <= 0:
            payment_payload.pop(event.from_user.id)
            await state.clear()
            await event.answer(
                ok=False,
                error_message="❌ Места закончились(\n\nЭтот тур больше недоступен.",
            )
            await surf_bot.delete_message(
                chat_id=event.from_user.id,
                message_id=event.id,
            )
            return
        payment_payload[event.from_user.id]['tour']['tour'] = tour
        await event.answer(ok=True)


@payment.message(F.successful_payment)
@inject
async def successful_payment(
        event: SuccessfulPayment,
        user_service: UserService = Provide[Container.user_service],
        payment_service: PaymentService = Provide[Container.payment_service],
        lesson_service: LessonService = Provide[Container.lesson_service],
        tour_service: TourService = Provide[Container.tour_service]
):
    payment_info: SuccessfulPayment = event.successful_payment
    payload_data: str = payment_info.invoice_payload
    if payload_data == "event: ApplyUserLessonBooking":
        lesson: dict = payment_payload[event.from_user.id]['lesson']['lesson']
        unicode: str = payment_payload[event.from_user.id]['lesson']['unicode']
        places: int = int(payment_payload[event.from_user.id]['lesson']['places'])
        price: int = int(payment_payload[event.from_user.id]['lesson']['price'])
        payment_payload.pop(event.from_user.id)

        user_entity = await user_service.get_user_by_tg_id(event.from_user.id)
        paid = await payment_service.create_surf_payment(
            tg_id=event.from_user.id, price=price, code=unicode
        )

        if paid:
            await lesson_service.reduce_places_on_lesson(code=unicode, count=places)
            result = [
                f"<b> 🎫 БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО 🎫</b>\n\n"
                f"🏄 <b>{lesson['type']}</b>\n"
                f"🗺 Направление: {lesson['dest']}\n"
                f"📝 Описание: {lesson['desc']}\n"
                f"⏰ Время начала: {lesson['time']}\n"
                f"⌛️ Продолжительность: {lesson['duration']}\n"
                f"📅 Дата: {lesson['start_date']}\n"
                f"👥 Забронированных мест: {places}\n"
                f"💶 Оплачено: {price}\n"
            ]

            pdf = await generate_invoice_pdf_lesson(
                user_name=user_entity['name'],
                lsn_type=lesson['type'],
                destination=lesson['dest'],
                start_date=lesson['start_date'],
                time=lesson['time'],
                duration=lesson['duration'],
                places=places,
                price=price,
            )

            pdf_file = BufferedInputFile(
                pdf.getvalue(),
                filename=f"Бронирование_{lesson['type']} | {lesson['start_date']} | {user_entity['name']}.pdf"
            )
            result.append(f"👨🏻‍💻 Пользователь: {user_entity['name']} (📞 {user_entity['phone']})")
            await safe_send_document(event.from_user.id, pdf_file)
            await event.answer(f"{'\n'.join(result)}", reply_markup=user_main_menu())
            await safe_send(
                text=f"🏄✅ НОВОЕ БРОНИРОВАНИЕ УРОКА:\n\n{'\n'.join(result)}",
                chat_id=NOTIFICATION_CHAT
            )
        else:
            await event.answer(
                text=f"<b>❌ При сохранении данных что-то пошло не так, "
                     f"однако оплата прошла и Ваш чек доступен Вам!</b>",
                reply_markup=user_main_menu()
            )

    elif payload_data == "event: ApplyUserTourBooking":
        tour: dict = payment_payload[event.from_user.id]['tour']['tour']
        tour_name: str = payment_payload[event.from_user.id]['tour']['tour_name']
        places: int = int(payment_payload[event.from_user.id]['tour']['places'])
        price: int = int(payment_payload[event.from_user.id]['tour']['price'])
        payment_payload.pop(event.from_user.id)

        user_entity = await user_service.get_user_by_tg_id(event.from_user.id)
        paid = await payment_service.create_tour_payment(
            tg_id=event.from_user.id, price=price, tour_name=tour_name
        )

        if paid:
            await tour_service.reduce_places_on_tour(tour_name=tour_name, count=places)
            result = [
                f"<b> 🎫 БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО 🎫</b>\n\n"
                f"🏕 {tour_name}\n"
                f"🗺 Направление: {tour['dest']}\n"
                f"📝 Описание: {tour['desc']}\n"
                f"⏰ Время начала: {tour['time']}\n"
                f"📅 Даты: {tour['start_date']} - {tour['end_date']}\n"
                f"👥 Забронированных мест: {places}\n"
                f"💶 Оплачено: {price}\n"
            ]

            pdf = await generate_invoice_pdf_tour(
                user_name=user_entity['name'],
                name=tour_name,
                destination=tour['dest'],
                start_date=tour['start_date'],
                time=tour['time'],
                end_date=tour['end_date'],
                places=places,
                price=price,
            )

            pdf_file = BufferedInputFile(
                file=pdf.getvalue(),
                filename=f"Бронирование_{tour_name} | {user_entity['name']}.pdf"
            )

            await safe_send_document(event.from_user.id, pdf_file)
            await event.answer(f"{'\n'.join(result)}", reply_markup=user_main_menu())
            await safe_send(
                text=f"🏕✅ НОВОЕ БРОНИРОВАНИЕ ТУРА:\n\n{'\n'.join(result)}",
                chat_id=NOTIFICATION_CHAT
            )
        else:
            await event.answer(
                text=f"При сохранении оплаты что-то пошло не так, "
                     f"однако оплата прошла и Ваш чек доступен Вам!",
                reply_markup=user_main_menu()
            )
