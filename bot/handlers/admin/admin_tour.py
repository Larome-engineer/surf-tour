from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.simple_calendar import SimpleCalendar

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_delete, answer_and_delete
from bot.keyboards.admin import *
from bot.notifications.user_notification import *
from database import service

admin_tour = Router()

headerAdd = "<b>🏄 ДОБАВЛЕНИЕ ТУРА 🏄</b>"
headerAddPlaces = "<b>👥 ТУР | ДОБАВЛЕНИЕ МЕСТ 👥 </b>"
headerRemove = "<b>🗑 УДАЛЕНИЕ ТУРА 🗑</b>"
headerList = "<b>📋 СПИСОК ТУРОВ 📋</b>"
headerByDirect = "<b>🔎 ПОИСК ТУРА ПО НАПРАВЛЕНИЮ 🔎</b>"


class AddTour(StatesGroup):
    direction = State()
    name = State()
    desc = State()
    places = State()
    start = State()
    end = State()
    time = State()
    price = State()


@admin_tour.callback_query(F.data == "AddTour", IsAdmin())
async def add_tour_start(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()
    if directions is None:
        await event.message.answer(
            text=f"{headerAdd}\n• Чтобы добавить тур, должно быть хотя бы 1 направление!",
            reply_markup=await tour_menu()
        )
    else:
        await event.message.answer(
            text=f"{headerAdd}\n• Выберите направление тура из доступных",
            reply_markup=await simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="DestForAdd_",
                back_callback="BackToTourMenu"
            )
        )
        await state.set_state(AddTour.direction)


@admin_tour.callback_query(F.data.startswith("DestForAdd_"), AddTour.direction, IsAdmin())
async def add_tour_dest(event: CallbackQuery, state: FSMContext):
    dest = event.data.split("_")[1]
    await answer_and_delete(event)

    await state.update_data(dest=dest)
    await event.message.answer(
        text=f"{headerAdd}\n• Отправьте название тура",
        reply_markup=await back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.name)


@admin_tour.message(AddTour.name, IsAdmin())
async def add_tour_name(event: Message, state: FSMContext):
    await state.update_data(name=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте описание тура",
        reply_markup=await back_to("Отмена добавления тура", "BackToTourMenu"))
    await state.set_state(AddTour.desc)


@admin_tour.message(AddTour.desc, IsAdmin())
async def add_tour_desc(event: Message, state: FSMContext):
    await state.update_data(desc=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте общее кол-во мест на тур",
        reply_markup=await back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.places)


@admin_tour.message(AddTour.places, IsAdmin())
async def add_tour_places(event: Message, state: FSMContext):
    await state.update_data(places=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте дату начала тура или отправьте /start для отмены",
        reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
    )
    await state.set_state(AddTour.start)


@admin_tour.callback_query(SimpleCalendarCallback.filter(), AddTour.start, IsAdmin())
async def add_tour_start_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        await event.message.delete()
        await state.update_data(start=date)

        await event.message.answer(
            text=f"{headerAdd}\n• Отправьте дату конца тура.\nДля отмены -> /start для отмены",
            reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
        )
        await state.set_state(AddTour.end)


@admin_tour.callback_query(SimpleCalendarCallback.filter(), AddTour.end, IsAdmin())
async def add_tour_end_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        data = await state.get_data()
        if date < data['start']:
            await event.message.answer(
                text=f"{headerAdd}\n• Дата окончания не может быть раньше даты начала. Пожалуйста, выберите заново.",
                reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
            )
            await state.set_state(AddTour.end)
            return
        await state.update_data(end=date)
        await event.message.delete()
        await event.message.answer(
            text=f"{headerAdd}\n• Отправьте время начала тура в формате: ЧЧ:MM",
            reply_markup=await back_to("Отмена добавления тура", "BackToTourMenu")
        )
        await state.set_state(AddTour.time)


@admin_tour.message(AddTour.time, IsAdmin())
async def add_tour_time(event: Message, state: FSMContext):
    await state.update_data(time=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте стоимость тура",
        reply_markup=await back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.price)


@admin_tour.message(AddTour.price, IsAdmin())
async def add_tour_price(event: Message, state: FSMContext):
    await state.update_data(price=event.text)
    tour_data = await state.get_data()
    await state.clear()
    tour = await service.create_tour(
        tour_name=tour_data['name'],
        tour_desc=tour_data['desc'],
        tour_places=tour_data['places'],
        start_date=tour_data['start'],
        start_time=tour_data['time'],
        end_date=tour_data['end'],
        tour_price=tour_data['price'],
        tour_destination=tour_data['dest']
    )
    if tour:
        await event.answer(
            text=f"{headerAdd}\n• Тур по направлению {tour_data['dest']} успешно создан",
            reply_markup=await tour_menu()
        )

        all_users = await service.get_all_users()
        for user in all_users:
            await event.bot.send_message(
                chat_id=int(user['tg_id']),
                text=f"🏕 <b>ОТКРЫЛСЯ НОВЫЙ ТУР!</b> 🏕\n\n"
                     f"• {tour_data['name']}\n"
                     f"• {tour_data['dest']}\n"
                     f"• {tour_data['start'].strftime("%d.%m.%Y")} - {tour_data['end'].strftime("%d.%m.%Y")} | {tour_data['time']}\n"
                     f"⬇️ Нажми, чтобы посмотреть подробности! ⬇️",
                reply_markup=one_button_callback(tour_data['name'], f"MoreAboutTour_{tour_data['name']}").as_markup()
            )
    else:
        await event.answer(
            text=f"{headerAdd}\n• При создании тура произошла ошибка",
            reply_markup=await tour_menu()
        )


@admin_tour.callback_query(F.data == "BookedTours", IsAdmin())
async def get_booked_tours(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    booked = await service.get_all_booked_tours()
    if booked is not None:
        result = [f"{headerList}\n"]
        for i, tour in enumerate(booked, start=1):
            result.append(
                f"<b>{i}. <code>{tour['Пользователь']}</code></b>\n"
                f"📝 {tour['Тур']}\n"
                f"👥 Цена: {tour['Цена']}"
            )
        await event.message.answer(f"{"\n".join(result)}", reply_markup=await tour_menu())
    else:
        await event.message.answer(
            text=f"{headerList}\n• Пока что нет забронированных туров",
            reply_markup=await tour_menu()
        )


@admin_tour.callback_query(F.data == "AllTourList", IsAdmin())
async def get_tours_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    tours = await service.get_all_tours()
    if tours is None:
        await event.message.answer(f"{headerList}\n• Пока нет туров", reply_markup=await tour_menu())
        return

    result = [f"{headerList}\nДля подробной информации нажми на нужный тур на клавиатуре\n\n"]
    for i, tour in enumerate(tours, start=1):
        result.append(
            f"<b>{i}. <code>{tour['name']}</code></b>\n"
            f"🔜 {tour['dest']}\n"
            f"🔜 Время начала{tour['time']}\n"
            f"📅 {tour['start_date']} - {tour['end_date']}\n"
        )

    await event.message.answer(
        text=f"{'\n'.join(result)}",
        reply_markup=await build_tours_pagination_keyboard(
            list_of_tours=tours,
            value_key="name",
            callback="InfoAboutTour_",
            back_callback="BackToTourMenu"
        )
    )


@admin_tour.callback_query(lambda c: (
        c.data.startswith("InfoAboutTour_page:") or
        c.data.startswith("InfoAboutTour_")
), IsAdmin())
async def get_tour_information(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    data = event.data
    tours = await service.get_all_tours()

    if "page:" in data:
        page = int(data.split(":")[-1])
        await event.message.answer(
            f"{headerList}\n • Страница {page + 1}",
            reply_markup=await build_tours_pagination_keyboard(
                list_of_tours=tours,
                value_key="name",
                callback="InfoAboutTour_",
                back_callback="BackToTourMenu",
                page=page,
            )
        )
        await event.answer()
    elif data.startswith("InfoAboutTour_"):
        tour_name = data.split("_")[1]
        tour = await service.get_tour_by_name(tour_name)
        if tour:
            result = (
                f"<b>{tour['name'].upper()}</b>\n\n"
                f"🔜 {tour['dest']}\n"
                f"📝 {tour['desc']}\n"
                f"👥 Места: {tour['places']}\n"
                f"⏰ Время начала: {tour['time']}\n"
                f"📅 {tour['start_date']} - {tour['end_date']}\n"
                f"💰 {str(tour['price'])}₽"
            )
            await event.message.answer(
                text=result,
                reply_markup=generate_entity_options(
                    list_of_text=["Добавить мест", "Удалить тур", "Назад"],
                    list_of_callback=["AddTourPlaces_", "DeleteTour_", "AllTourList"],
                    entity=tour,
                    entity_key="name"
                ).as_markup()
            )


@admin_tour.callback_query(F.data == "TourByDirection", IsAdmin())
async def get_tours_by_dest_start(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()
    if directions is not None:
        await event.message.answer(
            text=f"{headerByDirect}\n• Выберите выберите доступное направление",
            reply_markup=await simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="AdminSearchByDirection_",
                back_callback="BackToTourMenu"
            )
        )
    else:
        await event.message.answer("Пока нет направлений", reply_markup=await tour_menu())


@admin_tour.callback_query(F.data.startswith("AdminSearchByDirection_"), IsAdmin())
async def get_tours_by_dest_name(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split("_")[1]
    tours = await service.get_all_tour_by_dest(call)
    if tours is not None:
        result = [f"{headerList}\nДля подробной информации нажми на нужный тур на клавиатуре\n\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['name']}</code></b>\n"
                f"🔜 {tour['dest']}\n"
                f"🔜 Время начала{tour['time']}\n"
                f"📅 {tour['start_date']} - {tour['end_date']}\n"
            )
        await event.message.answer(
            text=f"{'\n'.join(result)}",
            reply_markup=await build_tours_pagination_keyboard(
                list_of_tours=tours,
                value_key="name",
                callback="InfoAboutTour_",
                back_callback="BackToTourMenu"
            )
        )
    else:
        await event.message.answer(f"{headerList}\n• Туров по направлению {call} нет", reply_markup=await tour_menu())


class AddTourPlaces(StatesGroup):
    places = State()


@admin_tour.callback_query(F.data.startswith("AddTourPlaces_"), IsAdmin())
async def add_tour_places_start(event: CallbackQuery, state: FSMContext):
    call = event.data.split("_")[1]
    await state.update_data(name=call)
    await answer_and_delete(event)
    await event.message.answer(
        text=f"{headerAddPlaces}\n• Введите кол-во добавляемых мест",
        reply_markup=await back_to("Отмена", "AllTourList")
    )
    await state.set_state(AddTourPlaces.places)


@admin_tour.message(AddTourPlaces.places, IsAdmin())
async def add_tour_places_choice(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    try:
        int(event.text)
    except ValueError:
        await event.answer(
            text=f"{headerAddPlaces}\n• Некорректное значение. Должно быть число\n\nВведите кол-во добавляемых мест",
            reply_markup=await back_to("Отмена", "AllTourList")
        )
        return
    add_places = await service.add_places_on_tour(state_data['name'], int(event.text))
    if add_places:
        users_list = await service.get_all_users_ids()
        if users_list is not None:
            send, not_send = await notify_about_places_tour(state_data['name'], users_list, int(event.text))
            await event.answer(
                text=f"{headerAddPlaces}\n• Места на тур {state_data['name']} успешно добавлены\n\n"
                     f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
                reply_markup=await tour_menu()
            )
        else:
            await event.answer(
                text=f"{headerAddPlaces}\n• Места на тур {state_data['name']} успешно добавлены\n"
                     f"/// База пользователей пуста для оповещения",
                reply_markup=await tour_menu()
            )
    else:
        await event.answer(
            text=f"{headerAddPlaces}\n• При добавлении мест что-то пошло не так",
            reply_markup=await tour_menu()
        )


@admin_tour.callback_query(F.data.startswith("DeleteTour_"), IsAdmin())
async def delete_tour(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split("_")[1]
    has_booked = await service.get_future_paid_tour(call)
    if has_booked is None:
        await event.message.answer(
            text=f"{headerRemove}\n• При удалении тура возникла ошибка",
            reply_markup=await tour_menu()
        )

    if has_booked:
        await event.message.answer(
            text=f"{headerRemove}\n• Нельзя удалять предстоящий тур, который приобрел хотя бы 1 человек!",
            reply_markup=await tour_menu())
        return

    deleted = await service.delete_tour(call)
    if deleted:
        await event.message.answer(
            text=f"{headerRemove}\n• Тур {call} успешно удален!",
            reply_markup=await tour_menu())
    else:
        await event.message.answer(
            text=f"{headerRemove}\n• При удалении тура возникла ошибка",
            reply_markup=await tour_menu()
        )
