from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import LabeledPrice
from dependency_injector.wiring import Provide, inject

from bot.config import PROVIDER_TOKEN
from bot.create import payment_payload
from DIcontainer import Container
from bot.handlers.handler_utils import *
from bot.keyboards.user import *
from service.user_service import UserService
from service.tour_service import TourService
from utils.validators import is_valid_email, is_valid_phone

user_tour = Router()

''' START BOOING TOUR'''


class UserBookTour(StatesGroup):
    tour = State()
    username = State()
    phone = State()
    email = State()
    exists = State()
    apply = State()


@user_tour.callback_query(F.data.startswith("StartBookingTour_"))
@inject
async def start_book_tour(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service],
        user_service: UserService = Provide[Container.user_service]
):
    await state.clear()
    await safe_answer(event)
    tour_name = event.data.split("_")[1]

    tour = await tour_service.get_tour_by_name(tour_name)
    if not tour:
        await safe_edit_text(event, "Такого тура не существует", user_main_menu())
        return
    if tour['places'] <= 0:
        await safe_edit_text(event, "Места на тур закончились", user_main_menu())
        return

    tour_naming = f"🎫<b>ТУР | БРОНИРОВАНИЕ </b>\nНаименование тура: {tour_name}"
    already_tour = await tour_service.get_user_tour_details(event.from_user.id, tour_name)

    if already_tour:
        await safe_edit_text(
            event,
            text=f"{tour_naming}\n\n❗️ Тур уже находится в списке предстоящих туров.",
            reply_markup=user_main_menu()
        )
        return

    await state.update_data(tour_name=tour_name, tour_naming=tour_naming)

    user_info = await user_service.get_user_by_tg_id(event.from_user.id)
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
@inject
async def book_tour_applying(
        event: Message | CallbackQuery,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service],
        tour_service: TourService = Provide[Container.tour_service]
):
    await safe_answer(event)
    data = await state.get_data()
    if isinstance(event, Message):
        phone = event.text
        now_state = await state.get_state()
        if now_state == "UserBookLesson:phone":
            if is_valid_phone(event.text):
                await state.update_data(phone=phone)
                if 'email' in data.keys() or 'phone' in data.keys() or 'name' in data.keys():
                    updated = await user_service.update_user(event.from_user.id, data['name'], data['email'], phone)
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
    tour_info = await tour_service.get_tour_by_name(data['tour_name'])
    price = tour_info['price'] * book_places

    await state.update_data(
        price=price,
        places=book_places,
        desc=tour_info['desc']
    )

    user_entity = await user_service.get_user_by_tg_id(event.from_user.id)
    text = (
        f"🎫 <b>ПОДТВЕРДЖЕНИЕ БРОНИРОВАНИЯ</b> 🎫\n\n"
        f"Участник:\n"
        f"🙋🏻 {user_entity['name']}\n\n"
        f"🏕 {tour_info['name']}\n"
        f"🗺 {tour_info['dest']}\n"
        f"📝 {tour_info['desc']}\n"
        f"👥 Кол-во бронируемых мест: {book_places}\n"
        f"⏰ Время начала: {tour_info['time']}\n"
        f"📅 С {tour_info['start_date'].strftime("%d.%m.%Y")} ПО {tour_info['end_date'].strftime("%d.%m.%Y")}\n"
        f"💶 {price}\n"
    )

    await send_by_instance(event, text=text, reply_markup=confirm_booking('ApplyUserTourBooking'))
    await state.set_state(UserBookTour.apply)


@user_tour.callback_query(F.data == "ApplyUserTourBooking", UserBookTour.apply)
async def book_tour_send_invoice(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
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


''' UPCOMING USERS TOURS '''


@user_tour.callback_query(F.data == "UpcomingUserTours")
@inject
async def upcoming_tours_list(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)
    user_tours = await tour_service.get_upcoming_user_tours(event.from_user.id)

    if not user_tours:
        await safe_edit_text(
            event,
            text=f"<b>✖️🏕 У Вас пока нет предстоящих туров туров</b>",
            reply_markup=user_account_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"<b>🏕🔜 ВАШИ ПРЕДСТОЯЩИЕ ТУРЫ </b>\n\n",
        reply_markup=build_tours_upcoming_pagination_keyboard(
            list_of_tours=user_tours,
            value_key='name',
            callback='UpcomingUserTours_',
            back_callback='UserAccount'
        )
    )


@user_tour.callback_query(F.data.startswith("UpcomingUserTours_"))
@inject
async def upcoming_tour_details(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)
    details = await tour_service.get_user_tour_details(event.from_user.id, event.data.split("_")[1])

    if event.data.startswith("UpcomingUserTours_page:"):
        user_tours = await tour_service.get_upcoming_user_tours(event.from_user.id)
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
        f"👥 Всего забронировано мест: 1\n"
        f"⏰ Время начала: {details['time']}\n"
        f"📅 С {details['start_date'].strftime("%d.%m.%Y")} ПО {details['end_date'].strftime("%d.%m.%Y")}\n"
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
@inject
async def tours_list(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)
    tours = await tour_service.get_all_tours_with_places()
    if not tours:
        await safe_edit_text(event, f"<b>✖️🏕 Пока нет туров</b>", reply_markup=user_main_menu())
        return

    await safe_edit_text(
        event,
        text="🏕 <b>СПИСОК ДОСТУПНЫХ ТУРОВ</b> 🏕\n"
             "• Для подробной информации нажми на нужный тур на клавиатуре\n\n",
        reply_markup=build_tours_pagination_keyboard(
            list_of_tours=tours,
            value_key='name',
            callback='MoreAboutTour_',
            back_callback='BackToUserMainMenu'
        )
    )


@user_tour.callback_query(F.data.startswith("MoreAboutTour_"))
@inject
async def tour_information(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)

    if event.data.startswith("MoreAboutTour_page:"):
        user_tours = await tour_service.get_all_tours_with_places()
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"🏕 <b>СПИСОК ДОСТУПНЫХ ТУРОВ</b> 🏕\n• Страница {page + 1}",
            reply_markup=build_tours_pagination_keyboard(
                list_of_tours=user_tours,
                page=page,
                callback="MoreAboutTour_",
                back_callback="UserAccount"
            )
        )
        return

    tour = await tour_service.get_tour_by_name(event.data.split('_')[1])

    if not tour:
        await safe_edit_text(event, f"<b>🏕✖️ Пока нет доступных туров</b>", reply_markup=user_main_menu())
        return

    result = [
        f"<b>🏕 {tour['name'].upper()}</b>\n\n"
        f"🗺 {tour['dest']}\n"
        f"📝 {tour['desc']}\n"
        f"👥 Свободные места: {tour['places']}\n"
        f"⏰ Время начала: {tour['time']}\n"
        f"📅 С {tour['start_date'].strftime("%d.%m.%Y")} ПО {tour['end_date'].strftime("%d.%m.%Y")}\n"
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
