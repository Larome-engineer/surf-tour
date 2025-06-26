from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendarCallback

import service
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from bot.notifications.user_notification import *
from aiogram.types import Message, CallbackQuery
from aiogram_calendar.simple_calendar import SimpleCalendar

from bot.filters.isAdmin import IsAdmin
from bot.keyboards.admin import *

admin = Router()


@admin.callback_query(F.data == "backtoadminmenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Админ-панель", reply_markup=main_menu().as_markup())


@admin.callback_query(F.data == "backtotouranddirect", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Туры и направления", reply_markup=tour_and_directions().as_markup())


@admin.callback_query(F.data == "backtousermenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("пользователи", reply_markup=user_menu().as_markup())


@admin.callback_query(F.data == "backtotourmenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Туры", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data == "backtodirectmenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Туры", reply_markup=direct_menu().as_markup())


class AddTour(StatesGroup):
    direction = State()
    name = State()
    desc = State()
    places = State()
    start = State()
    end = State()
    price = State()


@admin.callback_query(F.data == "addtour", IsAdmin())
async def add_tour(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    directions = await service.get_all_dest()
    if directions is None:
        await event.message.answer(
            text="<b>Чтобы добавить тур, должно быть хотя бы 1 навпрление</b>",
            reply_markup=tour_menu().as_markup()
        )
    else:
        builder = InlineKeyboardBuilder()
        for _ in directions:
            builder.row(InlineKeyboardButton(text=_, callback_data=f"dest_{_}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
        await event.message.answer("<b>Выберите направление тура из доступных</b>", reply_markup=builder.as_markup())
        await state.set_state(AddTour.direction)


@admin.callback_query(AddTour.direction, IsAdmin())
async def add_tour(event: CallbackQuery, state: FSMContext):
    dest = event.data.split("_")[1]
    await state.update_data(dest=dest)
    await event.answer()
    await event.message.delete()
    await event.message.answer("<b>Отправьте название тура</b>")
    await state.set_state(AddTour.name)


@admin.message(AddTour.name, IsAdmin())
async def add_tour(event: Message, state: FSMContext):
    await state.update_data(name=event.text)
    await event.answer("Отправьте описание тура")
    await state.set_state(AddTour.desc)


@admin.message(AddTour.desc, IsAdmin())
async def add_tour(event: Message, state: FSMContext):
    await state.update_data(desc=event.text)
    await event.answer("Отправьте общее кол-во мест на тур")
    await state.set_state(AddTour.places)


@admin.message(AddTour.places, IsAdmin())
async def add_tour(event: Message, state: FSMContext):
    await state.update_data(places=event.text)
    await event.answer("Отправьте дату начала тура", reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar())
    await state.set_state(AddTour.start)


@admin.callback_query(SimpleCalendarCallback.filter(), AddTour.start, IsAdmin())
async def add_start_tour(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        await state.update_data(start=date)
        await event.message.delete()
        await event.message.answer("Отправьте дату конца тура",
                                   reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar())
        await state.set_state(AddTour.end)


@admin.callback_query(SimpleCalendarCallback.filter(), AddTour.end, IsAdmin())
async def add_end_tour(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        await state.update_data(end=date)
        await event.message.delete()
        await event.message.answer("Отправьте стоимость тура")
        await state.set_state(AddTour.price)


@admin.message(AddTour.price, IsAdmin())
async def add_tour(event: Message, state: FSMContext):
    await state.update_data(price=event.text)
    tour_data = await state.get_data()
    await state.clear()
    tour = await service.create_tour(
        name=tour_data['name'],
        desc=tour_data['desc'],
        places=tour_data['places'],
        start=tour_data['start'],
        end=tour_data['end'],
        price=tour_data['price'],
        destination=tour_data['dest']
    )
    if tour:
        await event.answer(f"Тур по направлению {tour_data['dest']} успешно создан",
                           reply_markup=tour_menu().as_markup())
    else:
        await event.answer("При создани тура произошла ошибка", reply_markup=tour_menu().as_markup())


class AddDirection(StatesGroup):
    direction = State()


@admin.callback_query(F.data == "adddirection", IsAdmin())
async def add_direction_start(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("<b>Отправьте направление</b>")
    await state.set_state(AddDirection.direction)


@admin.message(AddDirection.direction, IsAdmin())
async def add_direction(event: Message, state: FSMContext):
    direction = await service.create_destination(event.text)
    if direction:
        await event.answer("Направление успешно создано!", reply_markup=direct_menu().as_markup())
    else:
        await event.answer(
            text="При создании направления что-то пошло не так\nПопробуйте еще раз",
            reply_markup=direct_menu().as_markup()
        )
    await state.clear()


class DeleteDirection(StatesGroup):
    dir_name = State()


@admin.callback_query(F.data == "deletedirection", IsAdmin())
async def delete_direction(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("ВНИМАНИЕ! При удалении направления, "
                               "удалятся все туры по этому направлению! "
                               "Хотите продолжить?", reply_markup=apply_delete_dir().as_markup())


@admin.callback_query(F.data.startswith("deletedir"), IsAdmin())
async def delete_direction(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    call = event.data.split("_")[1]
    if call == 'decline':
        await event.message.answer("Управление направлениями", reply_markup=direct_menu().as_markup())
    elif call == "apply":
        directions = await service.get_all_dest()
        if directions is not None:
            builder = InlineKeyboardBuilder()
            for _ in directions:
                builder.row(
                    InlineKeyboardButton(text=_, callback_data=f"directiondeleteadmin_{_}"))
            builder.row(InlineKeyboardButton(text="Назад", callback_data="backtodirectmenu"))
            await event.message.answer("Выберите направление для удаления", reply_markup=builder.as_markup())
            await state.set_state(DeleteDirection.dir_name)


@admin.callback_query(F.data.startswith("directiondeleteadmin_"), DeleteDirection.dir_name, IsAdmin())
async def delete_direction(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    call = event.data.split("_")[1]
    deleted = await service.delete_dest(call)
    if deleted:
        await event.message.answer(f"Навправление {call} успешно удалено", reply_markup=direct_menu().as_markup())
    else:
        await event.message.answer("При удалении наравления возникла ошибка", reply_markup=direct_menu().as_markup())


####### TOURS AND DIRECTIONS #######
@admin.callback_query(F.data == "bookedtours", IsAdmin())
async def booked_tours(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    booked = await service.get_all_booked_tours()
    if booked is not None:
        result = ["📋 <b>Список забронированных туров:</b>\n"]
        for i, tour in enumerate(booked, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['Пользователь']}</code></b>\n"
                f"📝 {tour['Тур']}\n"
                f"👥 Цена: {tour['Цена']}"
            )
        await event.message.answer(f"{"\n".join(result)}", reply_markup=tour_menu().as_markup())
    else:
        await event.message.answer(f"Пока что нет забронированных туров", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data == "toursanddirections", IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("<b>Опции туров и направлений</b>", reply_markup=tour_and_directions().as_markup())


@admin.callback_query(F.data.startswith('management'), IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()

    call = event.data.split("_")[1]
    if call == 'tour':
        await event.message.answer("Управление турами", reply_markup=tour_menu().as_markup())
    elif call == 'direct':
        await event.message.answer("Управление направлениями", reply_markup=direct_menu().as_markup())


@admin.callback_query(F.data == "tourlist", IsAdmin())
async def tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_all_tours()
    if tours is None:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=tour_menu().as_markup())
        return

    result = ["📋 <b>Список всех туров:</b>\n<i>Для подробной информации нажми на нужный тур на клавиатуре</i>\n\n"]
    for i, tour in enumerate(tours, start=1):
        result.append(
            f"<b>#{i}. <code>{tour['Название']}</code></b>\n"
            f"🔜 {tour['Направление']}\n"
            f"📅 {tour['Даты']}\n"
        )

    builder = InlineKeyboardBuilder()
    for _ in tours:
        builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"informtouradmin_{_['Название']}"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))

    await event.message.answer(f"{'\n'.join(result)}", reply_markup=builder.as_markup())


@admin.callback_query(F.data == "tourbydirect", IsAdmin())
async def tours_by_dest(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    directions = await service.get_all_dest()
    if directions is not None:
        builder = InlineKeyboardBuilder()
        for _ in directions:
            builder.row(
                InlineKeyboardButton(text=_, callback_data=f"searchbydirectionadmin_{_}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
        await event.message.answer("Выберите выберите доступное направлени", reply_markup=builder.as_markup())
    else:
        await event.message.answer("Пока нет направлений", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data.startswith("searchbydirectionadmin_"), IsAdmin())
async def tours_by_dest(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    call = event.data.split("_")[1]
    tours = await service.get_all_tour_by_dest(call)
    if tours is not None:
        result = ["📋 <b>Список всех туров</b>\n<i>Для подробной информации нажми на нужный тур на клавиатуре</i>\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['Название']}</code></b>\n"
                f"🔜 {tour['Направление']}\n"
                f"📅 {tour['Даты']}\n"
            )
        builder = InlineKeyboardBuilder()
        for _ in tours:
            builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"informtouradmin_{_['Название']}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=builder.as_markup())
    else:
        await event.message.answer("Туров по данному направлению пока нет", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data == "admintourinfo", IsAdmin())
async def tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_all_tours()
    if tours is not None:
        builder = InlineKeyboardBuilder()
        for _ in tours:
            builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"informtouradmin_{_['Название']}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
        await event.message.answer("Выберите тур для информации", reply_markup=builder.as_markup())
    else:
        await event.message.answer("На данный момент нет туров", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data.startswith("informtouradmin_"), IsAdmin())
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
        builder.row(
            InlineKeyboardButton(text="Добавить мест на тур", callback_data=f"addplacestouradmin_{tour['Название']}"),
            InlineKeyboardButton(text="Удалить тур", callback_data=f"tourtodeleteadmin_{tour['Название']}"),
            InlineKeyboardButton(text="Назад", callback_data="tourlist"),
            width=1
        )
        await event.message.answer(f"{"\n".join(result)}", reply_markup=builder.as_markup())
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data == "directionslist", IsAdmin())
async def directions_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    directions = await service.get_all_dest()
    if directions is not None:
        result = ["📋 <b>Список доступных направлений:</b>\n"]
        for i, direct in enumerate(directions, start=1):
            result.append(
                f"<b>#{i}. {direct}</b>"
            )
        await event.message.answer(text=f"{'\n'.join(result)}", reply_markup=direct_menu().as_markup())
    else:
        await event.message.answer(f"<b>Пока нет доступных направлений</b>", reply_markup=direct_menu().as_markup())


####### USERS #######
@admin.callback_query(F.data == "users", IsAdmin())
async def users(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("<b>Опции пользователя</b>", reply_markup=user_menu().as_markup())


class Mailing(StatesGroup):
    message = State()


@admin.callback_query(F.data == "usermailng", IsAdmin())
async def mailing(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("<b>Отправьте сообщение для рассылки</b>")
    await state.set_state(Mailing.message)


@admin.message(Mailing.message, IsAdmin())
async def send_mailing(event: Message, state: FSMContext):
    mailing_message = event.message_id
    await surf_bot.copy_message(
        chat_id=event.chat.id, from_chat_id=event.chat.id,
        message_id=mailing_message, reply_markup=confirm_mailing().as_markup()
    )

    await state.update_data(msg=mailing_message)


@admin.callback_query(F.data == 'decline_mailing')
async def decline_mailing(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Рассылка отменена", reply_markup=user_menu().as_markup())


@admin.callback_query(F.data == 'send_mailing')
async def mailing_handler(event: CallbackQuery, state: FSMContext):
    errors_count = 0
    good_count = 0
    data = await state.get_data()
    await state.clear()
    await event.answer()
    mailing_message = data['msg']
    user_list = await service.get_all_users_ids()
    if user_list is None or len(user_list) == 0:
        await event.answer()
        await event.message.delete()
        await event.message.answer(
            text="У Вас нет пользователей для рассылки сообщения",
            reply_markup=user_menu().as_markup()
        )
        return
    await event.message.delete()

    message = await event.message.answer("Рассылка начата...")
    for user in user_list:
        try:
            await surf_bot.copy_message(
                chat_id=user.user_tg_id,
                from_chat_id=event.from_user.id,
                message_id=mailing_message
            )
            good_count += 1
        except Exception as ex:
            errors_count += 1
            print(ex)

    await surf_bot.delete_message(chat_id=event.from_user.id, message_id=message.message_id)
    await event.message.answer(
        text=f"<b>Кол-во отосланных сообщений:</b> <code>{good_count}</code>\n"
             f"<b>Кол-во пользователей заблокировавших бота:</b> <code>{errors_count}</code>",
        reply_markup=user_menu().as_markup()
    )


@admin.callback_query(F.data == "userslist", IsAdmin())
async def get_all_users(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    user_list = await service.get_all_users()
    if user_list is not None:
        result = ["📋 <b>Список всех пользователей:</b>\n"]
        for i, user in enumerate(user_list, start=1):
            result.append(
                f"<b>#{i}. {user['Имя']}</code></b>\n"
                f"🔜<code>{user['Telegram ID']}</code>\n"
                f"📝 {user['Телефон']}\n"
                f"👥 {user['Почта']}\n"
            )
            await event.message.answer(f"{'\n'.join(result)}", reply_markup=user_menu().as_markup())
    else:
        await event.message.answer("В базе нет пользователей", reply_markup=user_menu().as_markup())


@admin.callback_query(F.data == "userinfo", IsAdmin())
async def user_get_info(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Выбери опцию поиска", reply_markup=user_info().as_markup())


class SearchUser(StatesGroup):
    telegram_id = State()
    email_or_phone = State()


@admin.callback_query(F.data == "searchbytgid", IsAdmin())
async def user_by_telegram_id(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Отправьте ID пользователя")
    await state.set_state(SearchUser.telegram_id)


@admin.message(SearchUser.telegram_id, IsAdmin())
async def user_by_telegram_id(event: Message, state: FSMContext):
    await state.clear()
    user = await service.get_user_by_tg_id(int(event.text))
    if user:
        tours = "\n".join([f"– {t.tour.tour_name}" for t in user.tours]) or "Нет туров"
        user = (
            f"👤 <b>{user.user_name}</b>\n"
            f"📧 {user.user_email}\n"
            f"📱 {user.user_phone}\n\n"
            f"🧳 <b>Тур(ы):</b>\n{tours}"
        )
        await event.answer(f"Пользователь:\n{user}", reply_markup=user_info().as_markup())
    else:
        await event.answer(f"Пользователь c id:\n{event.text} не существует", reply_markup=user_info().as_markup())


@admin.callback_query(F.data == "searchbyemailorphone", IsAdmin())
async def user_by_email_of_phone(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    await event.message.answer("Отправьте почту или номер телефона пользователя")
    await state.set_state(SearchUser.email_or_phone)


@admin.message(SearchUser.email_or_phone, IsAdmin())
async def user_by_email_of_phone(event: Message, state: FSMContext):
    await state.clear()
    user = await service.get_user_by_phone_or_email(event.text)
    if user:
        tours = "\n".join([f"– {t.tour.tour_name}" for t in user.tours]) or "Нет туров"
        user = (
            f"👤 <b>{user.user_name}</b>\n"
            f"📧 {user.user_email}\n"
            f"📱 {user.user_phone}\n\n"
            f"🧳 <b>Тур(ы):</b>\n{tours}"
        )
        await event.answer(f"Пользователь:\n{user}", reply_markup=user_info().as_markup())
    else:
        await event.answer(f"Такого пользователя не существует", reply_markup=user_info().as_markup())


class AddTourPlaces(StatesGroup):
    places = State()


# @admin.callback_query(F.data == "addtourplaces", IsAdmin())
# async def add_tour_places(event: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await event.answer()
#     await event.message.delete()
#     tours = await service.get_all_tours()
#     if tours is not None:
#         builder = InlineKeyboardBuilder()
#         for _ in tours:
#             builder.row(InlineKeyboardButton(text=_['Название'], callback_data=f"addplacestouradmin_{_['Название']}"))
#         builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
#         await event.message.answer("Выберите тур для информации", reply_markup=builder.as_markup())
#         await state.set_state(AddTourPlaces.name)
#     else:
#         await event.message.answer("На данный момент нет туров", reply_markup=tour_menu().as_markup())


@admin.callback_query(F.data.startswith("addplacestouradmin_"), IsAdmin())
async def add_tour_places(event: CallbackQuery, state: FSMContext):
    call = event.data.split("_")[1]
    await state.update_data(name=call)
    await event.answer()
    await event.message.delete()
    await event.message.answer(
        text="Введите кол-во добавляемых мест",
        reply_markup=back_to("Отмена", "tourlist").as_markup()
    )
    await state.set_state(AddTourPlaces.places)


@admin.message(AddTourPlaces.places, IsAdmin())
async def add_tour_places(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    add_places = await service.add_places_on_tour(state_data['name'], int(event.text))
    if add_places:
        users_list = await service.get_all_users_ids()
        if users_list is not None:
            send, not_send = await notify_about_places(users_list, state_data['name'], int(event.text))
            await event.answer(
                text=f"Места на тур {state_data['name']} успешно добавлены\n\n"
                     f"Кол-во человек, получивших уведомление: {send}\nНе получили: {not_send}",
                reply_markup=tour_menu().as_markup())
        else:
            await event.answer(
                text=f"Места на тур {state_data['name']} успешно добавлены\nБаза пользователей пуста для оповещения",
                reply_markup=tour_menu().as_markup())
    else:
        await event.answer("При добавлении мест что-то пошло не так", reply_markup=tour_menu().as_markup())


# class DeleteTour(StatesGroup):
#     tour_name = State()


# @admin.callback_query(F.data == "deletetour", IsAdmin())
# async def delete_tour(event: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await event.answer()
#     await event.message.delete()
#     tours = await service.get_all_tours()
#     if tours is not None:
#         builder = InlineKeyboardBuilder()
#         for _ in tours:
#             builder.row(
#                 InlineKeyboardButton(text=_['Название'], callback_data=f"tourtodeleteadmin_{_['Название']}"))
#         builder.row(InlineKeyboardButton(text="Назад", callback_data="backtotourmenu"))
#         await event.message.answer("Выберите тур для удаления", reply_markup=builder.as_markup())
#         await state.set_state(DeleteTour.tour_name)


@admin.callback_query(F.data.startswith("tourtodeleteadmin_"), IsAdmin())
async def delete_tour(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    call = event.data.split("_")[1]
    deleted = await service.delete_tour(call)
    if deleted:
        await event.message.answer(text=f"Тур {call} успешно удален!", reply_markup=tour_menu().as_markup())
    else:
        await event.message.answer(text=f"При удалении тура возникла ошибка", reply_markup=tour_menu().as_markup())


@admin.message(IsAdmin())
async def start(event: Message, state: FSMContext):
    await state.clear()
    await event.answer("<b>Админ панель</b>", reply_markup=main_menu().as_markup())
