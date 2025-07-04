from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment, BufferedInputFile

from bot.config import PROVIDER_TOKEN
from bot.handlers.handler_utils import clear_and_delete, answer_and_delete
from bot.keyboards.user import *
from database import service
from utils.generate_pdf import generate_invoice_pdf_tour
from utils.validators import is_valid_email, is_valid_phone

user_tour = Router()

payload_tour = {}


# --------------------
# BOOKING TOUR
# --------------------
class UserBookTour(StatesGroup):
    tour = State()
    username = State()
    phone = State()
    email = State()
    exists = State()
    apply = State()


@user_tour.callback_query(F.data.startswith("StartBookingTour_"))
async def book_tour(event: CallbackQuery, state: FSMContext):
    tour_name = event.data.split("_")[1]
    await answer_and_delete(event)

    t = await service.get_tour_by_name(tour_name)
    if t is None:
        await event.message.answer("Такого тура не существует")
        return
    if t['places'] <= 0:
        await event.message.answer("Места на тур закончились")
        return

    tour = await service.get_user_tour_details(event.from_user.id, tour_name)
    if tour is not None:
        await event.message.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование тура: {tour_name}\n\n"
                 f"Тур уже находится в списке предстоящих туров. ",
            reply_markup=user_main_menu().as_markup()
        )
        return

    await state.update_data(tour=tour_name)
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info['name'] is None or user_info['phone'] is None or user_info['email'] is None:
        await event.message.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование тура: {tour_name}\n\n"
                 f"Отправьте Ваше имя и фамилию",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
        )
        await state.set_state(UserBookTour.username)
    else:
        await state.set_state(UserBookTour.exists)
        await book_tour_applying(event, state)


@user_tour.message(UserBookTour.username)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.update_data(name=event.text)
    await event.answer(
        text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
             f"Наименование тура: {state_data['tour']}\n\n"
             f"Отправьте Ваш email",
        reply_markup=cancel_or_back_to(
            text="Отменить бронирование",
            callback="BackToUserMainMenu"
        ).as_markup()
    )
    await state.set_state(UserBookTour.email)


@user_tour.message(UserBookTour.email)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_email(event.text):
        await state.update_data(email=event.text)
        await event.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование тура: {state_data['tour']}\n\n"
                 f"Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
        )
        await state.set_state(UserBookTour.phone)
    else:
        await event.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование тура: {state_data['tour']}\n\n"
                 f"EMAIL {event.text} некорректный! Попробуйте ещё раз\n\nОтправьте Ваш email",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
        )
        await state.set_state(UserBookTour.email)


@user_tour.message(StateFilter(UserBookTour.phone, UserBookTour.exists))
async def book_tour_applying(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if isinstance(event, Message):
        phone = event.text
        now_state = await state.get_state()
        if now_state == "UserBookLesson:phone":
            if is_valid_phone(event.text):
                await state.update_data(phone=phone)
                if 'email' in data.keys() or 'phone' in data.keys() or 'name' in data.keys():
                    updated = await service.update_user(event.from_user.id, data['name'], data['email'], phone)
                    if not updated:
                        await state.clear()
                        await event.answer(
                            text="При заполнении Ваших данных что-то пошло не так. Попробуйте позднее",
                            reply_markup=user_main_menu().as_markup()
                        )
                        return
            else:
                await event.answer(
                    text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                         f"Наименование урока: {data['lesson']['type']}\n\n"
                         f"Номер телефона {event.text} некорректный! Попробуйте ещё раз\n\n"
                         f"Отправьте Ваш номер телефона",
                    reply_markup=cancel_or_back_to(
                        text="Отменить бронирование",
                        callback="BackToUserMainMenu"
                    ).as_markup()
                )
                await state.set_state(UserBookTour.phone)
                return

    book_places = 1
    tour_info = await service.get_tour_by_name(data['tour'])

    price = tour_info['price'] * book_places
    await state.update_data(price=price)
    await state.update_data(places=book_places)
    await state.update_data(desc=tour_info['desc'])
    user_entity = await service.get_user_by_tg_id(event.from_user.id)

    text = (
        f"🎫 <b>ПОДТВЕРДЖЕНИЕ БРОНИРОВАНИЯ</b> 🎫\n\n"
        f"Участник:\n"
        f"🙋🏻 {user_entity['name']}\n\n"
        f"🏕 {tour_info['name']}\n"
        f"🗺 {tour_info['dest']}\n"
        f"📝 {tour_info['desc']}\n"
        f"👥 Кол-во бронируемых мест: {book_places}\n"
        f"👥 Время начала: {tour_info['time']}\n"
        f"📅 {tour_info['start_date']} - {tour_info['end_date']}\n"
        f"💶 {price}\n"
    )

    if isinstance(event, CallbackQuery):
        await event.message.answer(
            text=text,
            reply_markup=confirm_booking('ApplyUserTourBooking').as_markup()
        )

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=confirm_booking('ApplyUserTourBooking').as_markup()
        )
    await state.set_state(UserBookTour.apply)


@user_tour.callback_query(F.data == "ApplyUserTourBooking", UserBookTour.apply)
async def book_tour_send_invoice(event: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    price: int = state_data['price']

    payload_tour[event.from_user.id] = {
        "places": state_data['places'],
        "price": price,
    }

    await event.answer()
    await event.message.delete()

    prices = [LabeledPrice(label=state_data['tour'], amount=price * 100)]
    await event.bot.send_invoice(
        chat_id=event.from_user.id,
        title=state_data['tour'],
        description=state_data['desc'],
        payload=f"{state_data['tour']} | {event.from_user.id}",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="tour_payment",
        need_name=True,
        need_phone_number=True,
        need_email=True
    )


@user_tour.pre_checkout_query()
async def process_pre_checkout(event: PreCheckoutQuery):
    tour_name = event.invoice_payload.split("|")[0].strip()
    tour = await service.get_tour_by_name(tour_name)
    if not tour or int(tour['places']) <= 0:
        await event.answer(
            ok=False,
            error_message="❌ Места закончились(\n\nЭтот тур больше недоступен.",
        )
        await event.bot.send_message(
            chat_id=event.from_user.id,
            text="Главное меню",
            reply_markup=user_main_menu().as_markup()
        )
        return
    await event.answer(ok=True)


@user_tour.message(F.successful_payment)
async def successful_payment(event: SuccessfulPayment):
    payment_info: SuccessfulPayment = event.successful_payment
    payload_data: str = payment_info.invoice_payload

    tour_name: str = payload_data.split("|")[0].strip()
    places: int = int(payload_tour[event.from_user.id]['places'])
    price: int = int(payload_tour[event.from_user.id]['price'])

    tour = await service.get_tour_by_name(tour_name)
    user_entity = await service.get_user_by_tg_id(event.from_user.id)

    paid = await service.create_tour_payment(
        tg_id=event.from_user.id, price=price, tour_name=tour_name
    )

    if paid:
        await service.reduce_places_on_tour(tour_name=tour_name, count=places)
        result = [f"<b> 🎫 БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО 🎫</b>\n\n"
                  f"🏕 {tour_name}\n"
                  f"🗺 {tour['dest']}\n"
                  f"🗺 {tour['desc']}\n"
                  f"Время: {tour['time']}\n"
                  f"📅 Даты: {tour['start_date']} - {tour['end_date']}\n"
                  f"👥 Забронированных мест: {places}\n"
                  f"💶 Оплачено: {price}\n"
                  ]

        pdf = await generate_invoice_pdf_tour(
            user_name=user_entity.user_name,
            name=tour_name,
            destination=tour['dest'],
            start_date=tour['start_date'],
            time=tour['time'],
            end_date=tour['end_date'],
            places=places,
            price=price,
        )

        pdf_file = BufferedInputFile(pdf.getvalue(),
                                     filename=f"Бронирование_{tour_name} | {user_entity['name']}.pdf")
        await event.bot.send_document(chat_id=event.from_user.id, document=pdf_file)
        await event.answer(f"{'\n'.join(result)}", reply_markup=user_main_menu().as_markup())
    else:
        await event.answer(
            text=f"При сохранении оплаты что-то пошло не так, однако оплата прошла и Ваш чек доступен Вам!",
            reply_markup=user_main_menu().as_markup()
        )


@user_tour.callback_query(F.data == "UpcomingUserTours")
async def upcoming_tours_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)

    tours = await service.get_upcoming_user_tours(event.from_user.id)

    if tours is not None and len(tours) != 0:
        result = [f"<b>🔜 ВАШИ ПРЕДСТОЯЩИЕ ТУРЫ 🔜</b>\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"🏕 {tour['name']}\n"
                f"🗺 {tour['dest']}\n"
                f"🗺 {tour['time']}\n"
                f"📅 {tour['start_date']} - {tour['end_date']}\n"
            )

        await event.message.answer(
            text=f"{'\n'.join(result)}",
            reply_markup=generate_keyboard(
                list_of_values=tours,
                value_key='name',
                callback='UpcomingUserTours_',
                back_callback='UserAccount'
            ).as_markup()
        )
    else:
        await event.message.answer(
            text=f"<b>У Вас пока нет предстоящих туров туров</b>",
            reply_markup=user_account_menu().as_markup()
        )


@user_tour.callback_query(F.data.startswith("UpcomingUserTours_"))
async def upcoming_tour_details(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    details = await service.get_user_tour_details(event.from_user.id, event.data.split("_")[1])

    text = (f"<b>🏕 {details['name']}</b>\n\n"
            f"🗺 {details['dest']}\n"
            f"📝 {details['desc']}\n"
            f"👥 Всего забронировано мест: {details['places']}\n"
            f"👥 Время начала: {details['time']}\n"
            f"📅 {details['start_date']} - {details['end_date']}\n"
            f"💶 {details['paid']}\n"
            )
    await event.message.answer(
        text=text,
        reply_markup=cancel_or_back_to(
            text="Назад",
            callback="upcomingUserTours"
        ).as_markup()
    )


@user_tour.callback_query(F.data == "AllToursWithFreePlaces")
async def tours_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    tours = await service.get_all_tours_with_places()
    if tours is not None:
        result = ["📋 <b>СПИСОК ДОСТУПНЫХ ТУРОВ:</b>\nДля подробной информации нажми на нужный тур на клавиатуре\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['name']}</code></b>\n"
                f"🗺 {tour['dest']}\n"
                f"👥 Свободные места: {tour['places']}\n"
                f"👥 Время начала: {tour['time']}\n"
                f"📅 Даты: {tour['start_date']} - {tour['end_date']}\n"
            )

        await event.message.answer(
            text=f"{'\n'.join(result)}",
            reply_markup=generate_keyboard(
                list_of_values=tours,
                value_key='name',
                callback='MoreAboutTour_',
                back_callback='BackToUserMainMenu'
            ).as_markup()
        )
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())


@user_tour.callback_query(F.data.startswith("MoreAboutTour_"))
async def tour_information(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split('_')[1]
    tour = await service.get_tour_by_name(call)
    if tour is not None:
        result = [f"<b>🏕 {tour['name'].upper()}</b>\n\n"
                  f"🗺 {tour['dest']}\n"
                  f"📝 {tour['desc']}\n"
                  f"👥 Свободные места: {tour['places']}\n"
                  f"👥 Время начала: {tour['time']}\n"
                  f"📅 {tour['start_date']} - {tour['end_date']}\n"
                  f"💶 {tour['price']}₽\n"
                  ]

        await event.message.answer(
            text=f"{"\n".join(result)}",
            reply_markup=generate_keyboard(
                text="Забронировать тур",
                callback="StartBookingTour_",
                value_key=tour['name'],
                back_callback="AllToursWithFreePlaces"
            ).as_markup()
        )
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())
