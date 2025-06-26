import datetime

from aiogram.fsm.state import StatesGroup, State

import service
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user import *
from utils.validators import is_valid_email, is_valid_phone

user = Router()


class UserBookTour(StatesGroup):
    tour = State()
    places = State()
    username = State()
    phone = State()
    email = State()
    apply = State()


@user.message(CommandStart())
async def start(event: Message, state: FSMContext):
    await state.clear()
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info is None:
        await service.create_user(tg_id=event.from_user.id)
    await event.answer("Добро пожаловать!", reply_markup=user_main_menu().as_markup())


@user.callback_query(F.data == "backtousermenu")
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Главное меню", reply_markup=user_main_menu().as_markup())


@user.callback_query(F.data == "backtouseraccount")
async def back_to_account(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info is not None:
        result = [f"<b>ID {user_info['id']}</b>\n\n"
                  f"👨🏻‍💻: {user_info['name'] if user_info['name'] is not None else "-"}\n"
                  f"📞: {user_info['phone'] if user_info['phone'] is not None else "-"}\n"
                  f"📧: {user_info['email'] if user_info['email'] is not None else "-"}\n"
                  ]
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=user_account_menu().as_markup())


@user.callback_query(F.data == "tourlistforuser")
async def tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_all_tours_with_places()
    if tours is not None:
        result = ["📋 <b>Список всех туров:</b>\n<i>Для подробной информации нажми на нужный тур на клавиатуре</i>\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['Название']}</code></b>\n"
                f"🔜 {tour['Направление']}\n"
                f"👥 Места: {tour['Места']}\n"
                f"📅 {tour['Даты']}\n"
            )
        builder = InlineKeyboardBuilder()
        for _ in tours:
            builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"informtouruser_{_['Название']}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtousermenu"))
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=builder.as_markup())
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())


@user.callback_query(F.data.startswith("informtouruser_"))
async def tour_information(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    call = event.data.split('_')[1]
    tour = await service.get_tour_by_name(call)
    if tour is not None:
        result = [f"<b>{tour['Название'].upper()}</b>\n\n"
                  f"🔜 {tour['Направление']}\n"
                  f"📝 {tour['Описание']}\n"
                  f"👥 Места: {tour['Места']}\n"
                  f"📅 {tour['Даты']}\n"
                  f"💰 {str(tour['Цена']) + "₽"}\n"
                  ]

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Забронировать тур", callback_data=f"booktouruser_{call}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtouseraccount"))

        await event.message.answer(f"{"\n".join(result)}", reply_markup=builder.as_markup())
        await state.set_state(UserBookTour.tour)
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())


@user.callback_query(F.data == "useraccount")
async def user_account(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info is not None:
        result = [f"<b>ID {user_info['id']}</b>\n\n"
                  f"👨🏻‍💻: {user_info['name'] if user_info['name'] is not None else "-"}\n"
                  f"📞: {user_info['phone'] if user_info['phone'] is not None else "-"}\n"
                  f"📧: {user_info['email'] if user_info['email'] is not None else "-"}\n"
                  ]
        await event.message.answer(f"{"\n".join(result)}", reply_markup=user_account_menu().as_markup())


@user.callback_query(F.data == "upcomingusertourlist")
async def upcoming_tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_upcoming_user_tours(event.from_user.id)
    if tours is not None and len(tours) != 0:
        result = []
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>ПРЕДСТОЯЩИЕ ТУРЫ</b>\n\n"
                f"🔜 {tour['tour_name']}\n"
                f"📝 {tour['destination']}\n"
                f"📝 Даты: {tour['start_date']} - {tour['end_date']}\n"
            )
        builder = InlineKeyboardBuilder()
        for _ in tours:
            builder.row(InlineKeyboardButton(text=_['tour_name'], callback_data=f"upcomigtouruser_{_['tour_name']}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtouseraccount"))
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=builder.as_markup())
    else:
        await event.message.answer(f"<b>У Вас пока нет предстоящих туров туров</b>",
                                   reply_markup=user_account_menu().as_markup())

@user.callback_query(F.data.startswith("upcomigtouruser_"))
async def upcoming_tour_details(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    details = await service.get_user_tour_details(event.from_user.id, event.data.split("_")[1])
    result = [f"<b>{details['tour_name']}</b>\n\n"
              f"🔜 {details['destination']}\n"
              f"📝 {details['description']}\n"
              f"👥 Кол-во мест: {details['places']}\n"
              f"📅 {details['start_date']} - {details['end_date']}\n"
              f"💰 {details['price_paid']}\n"
              ]
    await event.message.answer(
        text=f"{'\n'.join(result)}", reply_markup=user_account_menu().as_markup()
    )

@user.callback_query(F.data == "userbooktour")
async def book_tour(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_all_tours_with_places()
    if tours is not None:
        result = ["📋 <b>Список всех туров:</b>\n<i>Выберите 1 из доступных к бронировнию</i>\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['Название']}</code></b>\n"
                f"🔜 {tour['Направление']}\n"
                f"👥 Места: {tour['Места']}\n"
                f"📅 {tour['Даты']}\n"
            )
        builder = InlineKeyboardBuilder()
        for _ in tours:
            builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"booktouruser_{_['Название']}"))
        builder.row(InlineKeyboardButton(text="Отменить бронирование", callback_data="backtousermenu"))

        await event.message.answer(f"{'\n'.join(result)}", reply_markup=builder.as_markup())
        await state.set_state(UserBookTour.tour)
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())


@user.callback_query(UserBookTour.tour, F.data.startswith("booktouruser_"))
async def book_tour(event: CallbackQuery, state: FSMContext):
    call = event.data.split("_")[1]
    await state.update_data(tour=call)
    await event.answer()
    await event.message.delete()
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info['name'] is None or user_info['phone'] is None or user_info['email'] is None:
        await event.message.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {call}\n\n"
                 f"Как Вас зовут?", reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.username)

    else:
        await event.message.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {call}\n\nОтправьте кол-во бронируемых мест",
            reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.places)


@user.message(UserBookTour.username)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.update_data(name=event.text)
    await event.answer(
        text=f"БРОНИРОВАНИЕ\nНаименование тура: {state_data['tour']}\n\n"
             f"Отправьте Ваш email", reply_markup=cancel_book().as_markup()
    )
    await state.set_state(UserBookTour.email)


@user.message(UserBookTour.email)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_email(event.text):
        await state.update_data(email=event.text)
        await event.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {state_data['tour']}\n\n"
                 f"Отправьте Ваш номер телефона", reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.phone)
    else:
        await event.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {state_data['tour']}\n\n"
                 f"EMAIL {event.text} неккоректный! Попробуйте ещё раз\nОтправьте Ваш email",
            reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.email)


@user.message(UserBookTour.phone)
async def book_tour(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_phone(event.text):
        await state.update_data(phone=event.text)
        await event.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {state_data['tour']}\n\nОтправьте кол-во бронируемых мест",
            reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.places)
    else:
        await event.answer(
            text=f"БРОНИРОВАНИЕ\nНаименование тура: {state_data['tour']}\n\n"
                 f"Номер телефона {event.text} неккоректный! Попробуйте ещё раз\nОтправьте Ваш номер телефона",
            reply_markup=cancel_book().as_markup()
        )
        await state.set_state(UserBookTour.phone)


@user.message(UserBookTour.places)
async def book_tour(event: Message, state: FSMContext):
    data = await state.get_data()
    if 'email' in data.keys() or 'phone' in data.keys() or 'name' in data.keys():
        updated = await service.update_user(event.from_user.id, data['name'], data['email'], data['phone'])
        if not updated:
            await state.clear()
            await event.answer(
                text="При заполнении Ваших данных что-то пошло не так. Попробуйте позднее",
                reply_markup=user_main_menu().as_markup()
            )
            return

    tour = await service.get_tour_by_name(data['tour'])
    if tour['Места'] < int(event.text):
        await event.answer(f"Нельзя забронировать больше мест, чем доступно!\n"
                           "Попробуйте еще раз\n\n"
                           "БРОНИРОВАНИЕ\n"
                           f"Наименование тура: {data['tour']}\n"
                           "Отправьте кол-во бронируемых мест", reply_markup=cancel_book().as_markup())
        await state.set_state(UserBookTour.places)
    else:
        tour_info = await service.get_tour_by_name(data['tour'])
        num_of_places = int(event.text)
        price = tour_info['Цена'] * num_of_places

        await state.update_data(places=num_of_places)
        await state.update_data(price=price)

        result = [f"<b>ПОДТВЕРДЖЕНИЕ БРОНИРОВАНИЯ</b>\n\n"
                  f"🔜 {tour_info['Направление']}\n"
                  f"📝 {tour_info['Описание']}\n"
                  f"👥 Кол-во мест: {num_of_places}\n"
                  f"📅 {tour_info['Даты']}\n"
                  f"💰 {price}\n"
                  ]
        await event.answer(
            text=f"{'\n'.join(result)}", reply_markup=confirm_booking().as_markup()
        )
        await state.set_state(UserBookTour.apply)


@user.callback_query(F.data == "applyuserbooking", UserBookTour.apply)
async def book_tour(event: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    tour_name = state_data['tour']
    num_of_places = state_data['places']
    price = state_data['price']

    tour = await service.get_tour(tour_name)
    user_entity = await service.get_user(event.from_user.id)
    paid = await service.create_payment(
        price=price,
        user=user_entity, tour=tour, places=num_of_places
    )
    if paid:
        await service.reduce_places_on_tour(tour_name, num_of_places)
        user_tour = await service.get_user_tour_details(event.from_user.id, tour_name)
        result = [f"<b>БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО</b>\n\n"
                  f"🔜 {user_tour['tour_name']}\n"
                  f"📝 {user_tour['destination']}\n"
                  f"📝 Даты: {user_tour['start_date']} - {user_tour['end_date']}\n"
                  f"👥 Кол-во мест: {user_tour['places']}\n"
                  f"👥 Оплачено: {user_tour['price_paid']}\n"
                  ]
        await event.answer()
        await event.message.delete()
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=user_main_menu().as_markup())
    else:
        await event.message.answer(f"При оплате что-то пошло не так", reply_markup=user_main_menu().as_markup())
