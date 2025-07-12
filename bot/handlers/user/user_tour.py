from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice

from bot.config import PROVIDER_TOKEN
from bot.create import payment_payload
from bot.handlers.handler_utils import (
    edit_and_answer, send_by_instance, safe_answer,
    safe_delete, safe_edit_text, get_and_clear
)
from bot.keyboards.user import *
from database import service
from utils.validators import is_valid_email, is_valid_phone

user_tour = Router()


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
async def start_book_tour(event: CallbackQuery, state: FSMContext):
    await state.clear()
    tour_name = event.data.split("_")[1]

    tour = await service.get_tour_by_name(tour_name)
    if not tour:
        await edit_and_answer(event, "Такого тура не существует", user_main_menu())
        return
    if tour['places'] <= 0:
        await edit_and_answer(event, "Места на тур закончились", user_main_menu())
        return

    tour_naming = f"🎫<b>ТУР | БРОНИРОВАНИЕ </b>\nНаименование тура: {tour_name}"
    already_tour = await service.get_user_tour_details(event.from_user.id, tour_name)

    if already_tour:
        await edit_and_answer(
            event,
            text=f"{tour_naming}\n\n❗️ Тур уже находится в списке предстоящих туров.",
            reply_markup=user_main_menu()
        )
        return

    await state.update_data(tour_name=tour_name, tour_naming=tour_naming)

    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info['name'] is None or user_info['phone'] is None or user_info['email'] is None:
        await event.message.answer(
            text=f"{tour_naming}\n\n• Отправьте Ваше имя и фамилию",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
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
        text=f"{state_data['tour_naming']}\n\n• Отправьте Ваш email",
        reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
    )
    await state.set_state(UserBookTour.email)


@user_tour.message(UserBookTour.email)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_email(event.text):
        await state.update_data(email=event.text)
        await event.answer(
            text=f"{state_data['tour_naming']}\n\n• Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
        )
        await state.set_state(UserBookTour.phone)
    else:
        await event.answer(
            text=f"{state_data['tour_naming']}\n\n"
                 f"EMAIL <b>{event.text}</b> некорректный! Попробуйте ещё раз\n\n• Отправьте Ваш email",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
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
                            text=f"{data['tour_naming']}\n\n⛔️ При заполнении Ваших данных что-то пошло не так. Попробуйте позднее",
                            reply_markup=user_main_menu()
                        )
                        return
            else:
                await event.answer(
                    text=f"{data['tour_naming']}\n\n"
                         f"Номер телефона {event.text} некорректный! Попробуйте ещё раз\n\n• "
                         f"Отправьте Ваш номер телефона",
                    reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
                )
                await state.set_state(UserBookTour.phone)
                return

    book_places = 1
    tour_info = await service.get_tour_by_name(data['tour_name'])
    price = tour_info['price'] * book_places

    await state.update_data(
        price=price,
        places=book_places,
        desc=tour_info['desc']
    )

    user_entity = await service.get_user_by_tg_id(event.from_user.id)
    text = (
        f"🎫 <b>ПОДТВЕРДЖЕНИЕ БРОНИРОВАНИЯ</b> 🎫\n\n"
        f"Участник:\n"
        f"🙋🏻 {user_entity['name']}\n\n"
        f"🏕 {tour_info['name']}\n"
        f"🗺 {tour_info['dest']}\n"
        f"📝 {tour_info['desc']}\n"
        f"👥 Кол-во бронируемых мест: {book_places}\n"
        f"⏰ Время начала: {tour_info['time']}\n"
        f"📅 {tour_info['start_date']} - {tour_info['end_date']}\n"
        f"💶 {price}\n"
    )

    await send_by_instance(event, text=text, reply_markup=confirm_booking('ApplyUserTourBooking'))
    await state.set_state(UserBookTour.apply)


@user_tour.callback_query(F.data == "ApplyUserTourBooking", UserBookTour.apply)
async def book_tour_send_invoice(event: CallbackQuery, state: FSMContext):
    state_data = await get_and_clear(state)

    price: int = state_data['price']
    payment_payload[event.from_user.id] = {
        "tour": {
            "places": state_data['places'],
            "price": price,
            "tour_name": f"{state_data['tour_name']}"
        }
    }

    await safe_answer(event)
    await safe_delete(event)

    prices = [LabeledPrice(label=state_data['tour_name'], amount=price * 100)]
    await event.bot.send_invoice(
        chat_id=event.from_user.id,
        title=state_data['tour_name'],
        description=state_data['desc'],
        payload=f"event: {event.data}",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="tour_payment",
        need_name=True,
        need_phone_number=True,
        need_email=True
    )


# --------------------
# GETTER | UPCOMING
# --------------------
@user_tour.callback_query(F.data == "UpcomingUserTours")
async def upcoming_tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    user_tours = await service.get_upcoming_user_tours(event.from_user.id)

    if not user_tours:
        await edit_and_answer(
            event,
            text=f"<b>✖️🏕 У Вас пока нет предстоящих туров туров</b>",
            reply_markup=user_account_menu()
        )
        return

    result = [f"<b>🏕🔜 ВАШИ ПРЕДСТОЯЩИЕ ТУРЫ </b>\n\n"]
    # for i, tour in enumerate(user_tours, start=1):
    #     result.append(
    #         f"🏕 {tour['name']}\n"
    #         f"🗺 {tour['dest']}\n"
    #         f"🗺 {tour['time']}\n"
    #         f"📅 {tour['start_date']} - {tour['end_date']}\n"
    #     )

    await safe_edit_text(
        event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_tours_upcoming_pagination_keyboard(
            list_of_tours=user_tours,
            value_key='name',
            callback='UpcomingUserTours_',
            back_callback='UserAccount'
        )
    )


@user_tour.callback_query(F.data.startswith("UpcomingUserTours_"))
async def upcoming_tour_details(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    details = await service.get_user_tour_details(event.from_user.id, event.data.split("_")[1])

    if event.data.startswith("UpcomingUserTours_page:"):
        user_tours = await service.get_upcoming_user_tours(event.from_user.id)
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"<b>🏕🔜 ВАШИ ПРЕДСТОЯЩИЕ ТУРЫ </b>\n\n• Страница {page + 1}",
            reply_markup=build_tours_upcoming_pagination_keyboard(
                list_of_tours=user_tours,
                page=page,
                callback="MoreAboutTour_",
                back_callback="UserAccount"
            )
        )
        return

    text = (
        f"<b>🏕 {details['name']}</b>\n\n"
        f"🗺 {details['dest']}\n"
        f"📝 {details['desc']}\n"
        f"👥 Всего забронировано мест: {details['places']}\n"
        f"⏰ Время начала: {details['time']}\n"
        f"📅 {details['start_date']} - {details['end_date']}\n"
        f"💶 {details['paid']}\n"
    )

    await safe_edit_text(
        event,
        text=text,
        reply_markup=cancel_or_back_to(
            text="Назад",
            callback="UpcomingUserTours"
        )
    )


@user_tour.callback_query(F.data == "AllToursWithFreePlaces")
async def tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    tours = await service.get_all_tours_with_places()
    if not tours:
        await edit_and_answer(event, f"<b>✖️🏕 Пока нет туров</b>", reply_markup=user_main_menu())
        return

    result = [
        "🏕 <b>СПИСОК ДОСТУПНЫХ ТУРОВ</b> 🏕\n"
        "• Для подробной информации нажми на нужный тур на клавиатуре\n\n"
    ]

    # for i, tour in enumerate(tours, start=1):
    #     result.append(
    #         f"<b>#{i}. <code>{tour['name']}</code></b>\n"
    #         f"🗺 {tour['dest']}\n"
    #         f"👥 Свободные места: {tour['places']}\n"
    #         f"👥 Время начала: {tour['time']}\n"
    #         f"📅 Даты: {tour['start_date']} - {tour['end_date']}\n"
    #     )

    await safe_edit_text(
        event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_tours_pagination_keyboard(
            list_of_tours=tours,
            value_key='name',
            callback='MoreAboutTour_',
            back_callback='BackToUserMainMenu'
        )
    )


@user_tour.callback_query(F.data.startswith("MoreAboutTour_"))
async def tour_information(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    if event.data.startswith("MoreAboutTour_page:"):
        user_tours = await service.get_all_tours_with_places()
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"🏕 <b>СПИСОК ДОСТУПНЫХ ТУРОВ</b> 🏕</b>\n• Страница {page + 1}",
            reply_markup=build_tours_pagination_keyboard(
                list_of_tours=user_tours,
                page=page,
                callback="MoreAboutTour_",
                back_callback="UserAccount"
            )
        )
        return

    tour = await service.get_tour_by_name(event.data.split('_')[1])

    if not tour:
        await edit_and_answer(event, f"<b>🏕✖️ Пока нет доступных туров</b>", reply_markup=user_main_menu())
        return

    result = [
        f"<b>🏕 {tour['name'].upper()}</b>\n\n"
        f"🗺 {tour['dest']}\n"
        f"📝 {tour['desc']}\n"
        f"👥 Свободные места: {tour['places']}\n"
        f"⏰ Время начала: {tour['time']}\n"
        f"📅 {tour['start_date']} - {tour['end_date']}\n"
        f"💶 {tour['price']}₽\n"
    ]

    await safe_edit_text(
        event,
        text=f"{"\n".join(result)}",
        reply_markup=generate_keyboard(
            text="Забронировать тур",
            callback="StartBookingTour_",
            value_key=tour['name'],
            back_callback="AllToursWithFreePlaces"
        )
    )
