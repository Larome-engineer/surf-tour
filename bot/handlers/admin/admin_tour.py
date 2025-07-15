from aiogram import Router, F
from bot.keyboards.admin import *
from bot.handlers.handler_utils import *
from bot.filters.isAdmin import IsAdmin
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dependency_injector.wiring import Provide, inject
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from DIcontainer import Container


from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.simple_calendar import SimpleCalendar

from bot.notifications.user_notification import notify_about_tour, notify_places_tour
from service.destination_service import DestService
from service.export_service import ExportService
from service.tour_service import TourService
from service.user_service import UserService

admin_tour = Router()

ADD_TOUR = "<b>🏄 ДОБАВЛЕНИЕ ТУРА 🏄</b>"
ADD_PLACES = "<b>👥 ТУР | ДОБАВЛЕНИЕ МЕСТ 👥 </b>"
REMOVE = "<b>🗑 УДАЛЕНИЕ ТУРА 🗑</b>"
LIST = "<b>📋 СПИСОК ТУРОВ 📋</b>"
BY_DIRECT = "<b>🔎 ПОИСК ТУРА ПО НАПРАВЛЕНИЮ 🔎</b>"


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
@inject
async def add_tour_start(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service]
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()
    if directions is None:
        await safe_edit_text(
            event,
            text=f"{ADD_TOUR}\n• Чтобы добавить тур, должно быть хотя бы 1 направление!",
            reply_markup=tour_menu()
        )
    else:
        await safe_edit_text(
            event,
            text=f"{ADD_TOUR}\n• Выберите направление тура из доступных",
            reply_markup=simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="DestForAdd_",
                back_callback="BackToTourMenu"
            )
        )
        await state.set_state(AddTour.direction)


@admin_tour.callback_query(F.data.startswith("DestForAdd_"), AddTour.direction, IsAdmin())
async def add_tour_dest(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
    await state.update_data(dest=event.data.split("_")[1])
    await safe_edit_text(
        event,
        text=f"{ADD_TOUR}\n• Отправьте название тура",
        reply_markup=back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.name)


@admin_tour.message(AddTour.name, IsAdmin())
async def add_tour_name(event: Message, state: FSMContext):
    await state.update_data(name=event.text)
    await event.answer(
        text=f"{ADD_TOUR}\n• Отправьте описание тура",
        reply_markup=back_to("Отмена добавления тура", "BackToTourMenu"))
    await state.set_state(AddTour.desc)


@admin_tour.message(AddTour.desc, IsAdmin())
async def add_tour_desc(event: Message, state: FSMContext):
    await state.update_data(desc=event.text)
    await event.answer(
        text=f"{ADD_TOUR}\n• Отправьте общее кол-во мест на тур",
        reply_markup=back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.places)


@admin_tour.message(AddTour.places, IsAdmin())
async def add_tour_places(event: Message, state: FSMContext):
    if int(event.text) <= 0:
        await event.answer(
            text=f"{ADD_TOUR}\nКОЛ-ВО МЕСТ ДОЛЖНО БЫТЬ > 0\n\n• Отправьте общее кол-во мест на тур",
            reply_markup=back_to("Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddTour.places)
        return
    await state.update_data(places=event.text)
    await event.answer(
        text=f"{ADD_TOUR}\n• Отправьте дату начала тура или отправьте /start для отмены",
        reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
    )
    await state.set_state(AddTour.start)


@admin_tour.callback_query(SimpleCalendarCallback.filter(), AddTour.start, IsAdmin())
async def add_tour_start_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await safe_answer(event)
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        if date < datetime.now():
            await safe_edit_text(
                event,
                text=f"{ADD_TOUR}\nНЕПРАВИЛЬНАЯ ДАТА. ПОПРОБУЙТЕ ЕЩЕ РАЗ\n\n"
                     f"• Отправьте дату начала тура.\n-> Для отмены нажмите команду /start",
                reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
            )
            await state.set_state(AddTour.start)
            return
        await state.update_data(start=date)
        await safe_edit_text(
            event,
            text=f"{ADD_TOUR}\n• Отправьте дату конца тура.\nДля отмены -> /start для отмены",
            reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
        )
        await state.set_state(AddTour.end)


@admin_tour.callback_query(SimpleCalendarCallback.filter(), AddTour.end, IsAdmin())
async def add_tour_end_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await safe_answer(event)
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        data = await state.get_data()
        if date < data['start']:
            await safe_edit_text(
                event,
                text=f"{ADD_TOUR}\n• Дата окончания не может быть раньше даты начала. Пожалуйста, выберите заново.",
                reply_markup=SimpleCalendar(locale="ru_RU").start_calendar()
            )
            await state.set_state(AddTour.end)
            return

        await state.update_data(end=date)
        await safe_edit_text(
            event,
            text=f"{ADD_TOUR}\n• Отправьте время начала тура в формате: ЧЧ:MM",
            reply_markup=back_to("Отмена добавления тура", "BackToTourMenu")
        )
        await state.set_state(AddTour.time)


@admin_tour.message(AddTour.time, IsAdmin())
async def add_tour_time(event: Message, state: FSMContext):
    await state.update_data(time=event.text)
    await event.answer(
        text=f"{ADD_TOUR}\n• Отправьте стоимость тура",
        reply_markup=back_to("Отмена добавления тура", "BackToTourMenu")
    )
    await state.set_state(AddTour.price)


@admin_tour.message(AddTour.price, IsAdmin())
@inject
async def add_tour_price(
        event: Message,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service],
        user_service: UserService = Provide[Container.user_service]
):
    tour_data = await get_and_clear(state)

    tour = await tour_service.create_tour(
        tour_name=tour_data['name'],
        tour_desc=tour_data['desc'],
        tour_places=tour_data['places'],
        start_date=tour_data['start'],
        start_time=tour_data['time'],
        end_date=tour_data['end'],
        tour_price=int(event.text),
        tour_destination=tour_data['dest']
    )

    if not tour:
        await event.answer(
            text=f"{ADD_TOUR}\n• При создании тура произошла ошибка",
            reply_markup=tour_menu()
        )
        return

    all_users = await user_service.get_all_users()
    if not all_users:
        await event.answer(
            text=f"{ADD_TOUR}\n• Тур по направлению {tour_data['dest']} успешно создан\n"
                 f"/// База пользователей пуста для оповещения",
            reply_markup=tour_menu()
        )
        return

    send, not_send = await notify_about_tour(tour=tour_data, users=all_users)
    await event.answer(
        text=f"{ADD_TOUR}\n• Тур по направлению {tour_data['dest']} успешно создан\n"
             f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
        reply_markup=tour_menu()
    )


@admin_tour.callback_query(F.data == "BookedTours", IsAdmin())
@inject
async def get_booked_tours(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)

    booked = await tour_service.get_all_booked_tours()
    if not booked:
        await safe_edit_text(
            event,
            text=f"{LIST}\n• Пока что нет забронированных туров",
            reply_markup=tour_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{LIST}\n",
        reply_markup=build_tours_pagination_keyboard(
            list_of_tours=booked,
            back_callback="BackToTourMenu"
        ))


@admin_tour.callback_query(F.data == "AllTourList", IsAdmin())
@inject
async def get_tours_list(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)

    tours = await tour_service.get_all_tours_with_places()
    if not tours:
        await safe_edit_text(event, f"{LIST}\n• Пока нет туров", reply_markup=tour_menu())
        return

    await safe_edit_text(
        event,
        text=f"{LIST}\nДля подробной информации нажми на нужный тур на клавиатуре\n\n",
        reply_markup=build_tours_pagination_keyboard(
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
@inject
async def get_tour_information(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)

    data = event.data
    tours = await tour_service.get_all_tours_with_places()

    if "page:" in data:
        page = int(data.split(":")[-1])
        await safe_edit_text(
            event,
            f"{LIST}\n • Страница {page + 1}",
            reply_markup=build_tours_pagination_keyboard(
                list_of_tours=tours,
                value_key="name",
                callback="InfoAboutTour_",
                back_callback="BackToTourMenu",
                page=page,
            )
        )
    elif data.startswith("InfoAboutTour_"):
        tour_name = data.split("_")[1]
        tour = await tour_service.get_tour_by_name(tour_name)
        if tour:
            result = (
                f"<b>{tour['name'].upper()}</b>\n\n"
                f"🔜 {tour['dest']}\n"
                f"📝 {tour['desc']}\n"
                f"👥 Места: {tour['places']}\n"
                f"⏰ Время начала: {tour['time']}\n"
                f"📅 {tour['start_date'].strftime("%d.%m.%Y")} - {tour['end_date'].strftime("%d.%m.%Y")}\n"
                f"💰 {str(tour['price'])}₽"
            )
            await safe_edit_text(
                event,
                text=result,
                reply_markup=generate_entity_options(
                    list_of_text=["Добавить мест", "Удалить тур", "Назад"],
                    list_of_callback=["AddTourPlaces_", "DeleteTour_", "AllTourList"],
                    entity=tour,
                    entity_key="name"
                )
            )


@admin_tour.callback_query(F.data == "TourByDirection", IsAdmin())
@inject
async def get_tours_by_dest_start(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service]
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()
    if not directions:
        await safe_edit_text(event, "Пока нет направлений", reply_markup=tour_menu())
        return
    await safe_edit_text(
        event,
        text=f"{BY_DIRECT}\n• Выберите доступное направление",
        reply_markup=simple_build_dynamic_keyboard(
            list_of_values=directions,
            value_key="name",
            callback="AdminSearchByDirection_",
            back_callback="BackToTourMenu"
        )
    )


@admin_tour.callback_query(F.data.startswith("AdminSearchByDirection_"), IsAdmin())
@inject
async def get_tours_by_dest_name(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)
    call = event.data.split("_")[1]
    tours = await tour_service.get_all_tour_by_dest(call)
    if not tours:
        await safe_edit_text(event, f"{LIST}\n• Туров по направлению {call} нет", reply_markup=tour_menu())
        return

    await safe_edit_text(
        event,
        text=f"{LIST}\nДля подробной информации нажми на нужный тур на клавиатуре\n\n",
        reply_markup=build_tours_pagination_keyboard(
            list_of_tours=tours,
            value_key="name",
            callback="InfoAboutTour_",
            back_callback="BackToTourMenu"
        )
    )


class AddTourPlaces(StatesGroup):
    places = State()


@admin_tour.callback_query(F.data.startswith("AddTourPlaces_"), IsAdmin())
async def add_tour_places_start(event: CallbackQuery, state: FSMContext):
    await state.update_data(name=event.data.split("_")[1])
    await safe_answer(event)
    await safe_edit_text(
        event,
        text=f"{ADD_PLACES}\n• Введите кол-во добавляемых мест",
        reply_markup=back_to("Отмена", "AllTourList")
    )
    await state.set_state(AddTourPlaces.places)


@admin_tour.message(AddTourPlaces.places, IsAdmin())
@inject
async def add_tour_places_choice(
        event: Message,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service],
        user_service: UserService = Provide[Container.user_service]
):
    state_data = await get_and_clear(state)

    try:
        int(event.text)
    except ValueError:
        await event.answer(
            text=f"{ADD_PLACES}\n• Некорректное значение. Должно быть число\n\n"
                 f"Введите кол-во добавляемых мест",
            reply_markup=back_to("Отмена", "AllTourList")
        )
        return

    add_places = await tour_service.add_places_on_tour(state_data['name'], int(event.text))
    if not add_places:
        await event.answer(
            text=f"{ADD_PLACES}\n• При добавлении мест что-то пошло не так",
            reply_markup=tour_menu()
        )
        return

    tour = await tour_service.get_tour_by_name(state_data['name'])
    users_list = await user_service.get_all_users_ids()
    if not users_list:
        await event.answer(
            text=f"{ADD_PLACES}\n• Места на тур {state_data['name']} успешно добавлены\n"
                 f"/// База пользователей пуста для оповещения",
            reply_markup=tour_menu()
        )
        return

    send, not_send = await notify_places_tour(tour, users_list, int(event.text))
    await event.answer(
        text=f"{ADD_PLACES}\n• Места на тур {state_data['name']} успешно добавлены\n\n"
             f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
        reply_markup=tour_menu()
    )


@admin_tour.callback_query(F.data.startswith("DeleteTour_"), IsAdmin())
@inject
async def delete_tour(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await state.clear()
    await safe_answer(event)

    tour_name = event.data.split("_")[1]

    has_booked = await tour_service.get_future_paid_tour(tour_name)
    if has_booked:
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Нельзя удалять предстоящий тур, который приобрел хотя бы 1 человек!",
            reply_markup=tour_menu())
        return

    await state.update_data(name=tour_name)
    await safe_edit_text(
        event,
        text=f"{REMOVE}\n• Желайте сделать экспорт базы данных перед удалением?",
        reply_markup=any_button_kb(
            text=["Да", "Нет"],
            callback=["ToRemoveTour_yes", "ToRemoveTour_no"]
        )
    )
    return


@admin_tour.callback_query(F.data.startswith("ToRemoveTour_"), IsAdmin())
@inject
async def yes_to_remove_lesson(
        event: CallbackQuery,
        state: FSMContext,
        tour_service: TourService = Provide[Container.tour_service]
):
    await safe_answer(event)
    data = await get_and_clear(state)
    answer = event.data.split("_")[1]

    if answer == "yes":
        export = await ExportService.export_db()
        if not export:
            await safe_edit_text(
                event,
                "<b>💻 ТУР | МЕНЮ 💻</b>\n\nТур НЕ удален!\nПроизошла ошибка при экспорте данных",
                reply_markup=tour_menu()
            )
            return

        await safe_delete(event)
        filename = f"backup_{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}.xlsx"
        await event.message.answer_document(
            document=BufferedInputFile(export.read(), filename=filename),
            caption="📦 Бэкап данных."
        )

    deleted = await tour_service.delete_tour(data['name'])
    if not deleted:
        if answer == "yes":
            await event.message.answer(
                text=f"{REMOVE}\n• При удалении тура возникла ошибка",
                reply_markup=tour_menu()
            )
            return
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• При удалении тура возникла ошибка",
            reply_markup=tour_menu()
        )
        return

    if answer == "yes":
        await event.message.answer(
            text=f"{REMOVE}\n• Тур {data['name']} успешно удален!",
            reply_markup=tour_menu()
        )
        return
    await safe_edit_text(
        event,
        text=f"{REMOVE}\n• Тур {data['name']} успешно удален!",
        reply_markup=tour_menu()
    )
