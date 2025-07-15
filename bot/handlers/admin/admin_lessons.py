from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.simple_calendar import SimpleCalendar
from dependency_injector.wiring import Provide, inject

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import *
from bot.keyboards.admin import *
from bot.notifications.user_notification import *
from service.destination_service import DestService
from service.export_service import ExportService
from service.lesson_service import LessonService
from service.user_service import UserService
from utils.validators import is_valid_time
from DIcontainer import Container
admin_lessons = Router()

ADD_LESSON = "<b>🏄 ДОБАВЛЕНИЕ УРОКА 🏄</b>"
ADD_PLACES = "<b>👥 УРОК | ДОБАВЛЕНИЕ МЕСТ 👥 </b>"
REMOVE = "<b>🗑 УДАЛЕНИЕ УРОКА 🗑</b>"
LESSON_LIST = "<b>📋 СПИСОК УРОКОВ 📋</b>"
ADD_TYPE = "<b>✏️ ДОБАВЛЕНИЕ ТИПА УРОКА ✏️</b>"


# --------------------
# CREATE LESSON
# --------------------
class AddLesson(StatesGroup):
    direction = State()
    duration = State()
    lesson_type = State()
    desc = State()
    places = State()
    start = State()
    end = State()
    time = State()
    price = State()


@admin_lessons.callback_query(F.data == "AddLesson", IsAdmin())
@inject
async def add_lesson_start(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service],
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()
    types = await lesson_service.get_lesson_types()
    if not directions:
        await safe_edit_text(
            event,
            text=f"{ADD_LESSON}\n• Чтобы добавить урок, должно быть хотя бы 1 направление",
            reply_markup=lesson_menu()
        )

    if not types:
        await safe_edit_text(
            event,
            text=f"{ADD_LESSON}\n• Чтобы добавить урок должен быть хотя бы 1 тип урока",
            reply_markup=lesson_menu()
        )

    else:
        await safe_edit_text(
            event,
            text=f"{ADD_LESSON}\n• Выберите направление урока из доступных",
            reply_markup=simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="SelectDestWhenAddLesson_",
                back_callback="BackToLessonMenu"
            )
        )
        await state.set_state(AddLesson.direction)


@admin_lessons.callback_query(F.data.startswith("SelectDestWhenAddLesson_"), AddLesson.direction, IsAdmin())
@inject
async def add_lesson_choice(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await safe_answer(event)
    await state.update_data(dest=event.data.split("_")[1])

    lesson_types = await lesson_service.get_lesson_types()
    if lesson_types is None:
        await state.clear()
        await safe_edit_text(
            event,
            text=f"{ADD_LESSON}\n• Пока не существует ни одного типа урока",
            reply_markup=lesson_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{ADD_LESSON}Выберите тип урока",
        reply_markup=buttons_by_entity_list_values(
            entity_list=lesson_types,
            callback="GetLessonType_",
            back_to_callback="BackToLessonMenu"
        )
    )
    await state.set_state(AddLesson.lesson_type)


@admin_lessons.callback_query(F.data.startswith("GetLessonType_"), AddLesson.lesson_type, IsAdmin())
async def add_lesson_type(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
    await state.update_data(type=event.data.split("_")[1])
    await safe_edit_text(
        event,
        text=f"{ADD_LESSON}\n• Отправьте описание урока",
        reply_markup=back_to("Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.desc)


@admin_lessons.message(AddLesson.desc, IsAdmin())
async def add_lesson_description(event: Message, state: FSMContext):
    await state.update_data(desc=event.text)
    await event.answer(
        text=f"{ADD_LESSON}\n• Отправьте общее кол-во мест на урок",
        reply_markup=back_to("Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.places)


@admin_lessons.message(AddLesson.places, IsAdmin())
async def add_lesson_places(event: Message, state: FSMContext):
    if int(event.text) <= 0:
        await event.answer(
            text=f"{ADD_LESSON}\nКОЛ-ВО МЕСТ ДОЛЖНО БЫТЬ > 0\n\n• Отправьте общее кол-во мест на урок",
            reply_markup=back_to("Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddLesson.places)
        return
    await state.update_data(places=event.text)
    await event.answer(
        text=f"{ADD_LESSON}\n• Отправьте дату начала урока.\n-> Для отмены нажмите команду /start",
        reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
    )
    await state.set_state(AddLesson.start)


@admin_lessons.callback_query(SimpleCalendarCallback.filter(), AddLesson.start, IsAdmin())
async def add_lesson_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    await safe_answer(event)
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        if date < datetime.now():
            await safe_edit_text(
                event,
                text=f"{ADD_LESSON}\nНЕПРАВИЛЬНАЯ ДАТА. ПОПРОБУЙТЕ ЕЩЕ РАЗ\n\n"
                     f"• Отправьте дату начала урока.\n-> Для отмены нажмите команду /start",
                reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
            )
            await state.set_state(AddLesson.start)
            return
        await state.update_data(start=date)
        await safe_edit_text(
            event,
            text=f"{ADD_LESSON}\n• Отправьте время начала урока в формате: ЧЧ:MM\n<u>Пример: 10:00</u>",
            reply_markup=back_to("Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddLesson.time)



@admin_lessons.message(AddLesson.time, IsAdmin())
async def add_lesson_time(event: Message, state: FSMContext):
    if is_valid_time(event.text):
        await state.update_data(time=event.text)
        await event.answer(
            text=f"{ADD_LESSON}\n• Отправьте продолжительность урока в формате: Xч Y мин\n<u>Пример: 2ч 30 мин.</u>",
            reply_markup=back_to(text="Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddLesson.duration)
    else:
        await event.answer(
            text=f"{ADD_LESSON}\n• Некорректный формат ввода времени. Формат должен быть ЧЧ:MM!\n"
                 f"<u>Пример: 10:00</u>\nПопробуй ещё раз: Отправь время начала урок"
        )
        await state.set_state(AddLesson.time)


@admin_lessons.message(AddLesson.duration, IsAdmin())
async def add_lesson_price(event: Message, state: FSMContext):
    await state.update_data(duration=event.text)
    await event.answer(
        text=f"{ADD_LESSON}\n• Отправьте стоимость урока",
        reply_markup=back_to(text="Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.price)


@admin_lessons.message(AddLesson.price, IsAdmin())
@inject
async def add_lesson_create(
        event: Message,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service],
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    lesson_data = await get_and_clear(state)

    lesson = await lesson_service.create_lesson(
        desc=lesson_data['desc'],
        duration=lesson_data['duration'],
        places=lesson_data['places'],
        start=lesson_data['start'],
        time=lesson_data['time'],
        lesson_type=lesson_data['type'].capitalize(),
        price=int(event.text),
        dest=lesson_data['dest']
    )

    created = lesson[0]

    if not created:
        await event.answer(
            text=f"{ADD_LESSON}\n• При создании урока произошла ошибка",
            reply_markup=lesson_menu()
        )
        return
    lesson_data['unicode'] = lesson[1]
    lsn = btn_perform(
        lesson_data['type'].capitalize(),
        lesson_data['start'],
        lesson_data['time']
    )

    all_users = await user_service.get_all_users()
    if not all_users:
        await event.answer(
            text=f"{ADD_LESSON}\n• Урок успешно добавлен!\n\n"
                 f"/// База пользователей пуста для оповещения",
            reply_markup=lesson_menu()
        )
        return

    send, not_send = await notify_about_lesson(
        lesson=lesson_data,
        users=all_users
    )
    await event.answer(
        text=f"{ADD_LESSON}\n• Урок успешно добавлен!\n\n"
             f"> {lsn}\n"
             f"> Направление {lesson_data['dest']}\n\n"
             f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
        reply_markup=lesson_menu())


# --------------------
# GET LESSON
# --------------------
@admin_lessons.callback_query(F.data == "BookedLessons", IsAdmin())
@inject
async def get_all_booked_lessons(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await state.clear()
    await safe_answer(event)
    booked = await lesson_service.get_all_booked_lessons_future()
    if not booked:
        await safe_edit_text(
            event,
            f"{LESSON_LIST}\n❌ Нет предстоящих забронированных уроков.",
            reply_markup=lesson_menu()
        )
        return

    # Отправляем частями
    await safe_edit_text(
        event,
        text=f"{LESSON_LIST}\n• Список предстоящих забронированных уроков\n",
        reply_markup=build_lessons_pagination_keyboard(
            lessons=booked,
            page=0,
            back_callback="BackToLessonMenu"
        )
    )


@admin_lessons.callback_query(F.data == "AllLessonList", IsAdmin())
@inject
async def get_all_lessons(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await state.clear()
    await safe_answer(event)

    lessons = await lesson_service.get_all_lessons()
    if not lessons:
        await safe_edit_text(
            event=event,
            text=f"{LESSON_LIST}\n• Пока нет уроков",
            reply_markup=lesson_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{LESSON_LIST}\nДля подробной информации нажми на нужный урок на клавиатуре\n",
        reply_markup=build_lessons_pagination_keyboard(
            lessons=lessons,
            back_callback="BackToLessonMenu"
        )
    )


@admin_lessons.callback_query(lambda c: (
        c.data.startswith("LessonsList_page:") or
        c.data.startswith("InfoAboutLesson_")
), IsAdmin())
@inject
async def get_lesson_by_code(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await state.clear()
    await safe_answer(event)

    data = event.data
    lessons = await lesson_service.get_all_lessons()

    if data.startswith("LessonsList_page:"):
        page = int(data.split(":")[1])
        await safe_edit_text(
            event,
            f"{LESSON_LIST}\n<b>• Страница {page + 1}</b>",
            reply_markup=build_lessons_pagination_keyboard(
                lessons=lessons,
                page=page,
                back_callback="BackToLessonMenu"
            )
        )
    elif data.startswith("InfoAboutLesson_"):
        lesson = await lesson_service.get_lesson_by_code(data.split("_")[1])
        if lesson:
            result = (
                f"<b>{lesson['type'].upper()}</b>\n\n"
                f"🗺 {lesson['dest']}\n"
                f"📝 {lesson['desc']}\n"
                f"👥 Осталось мест: {lesson['places']}\n"
                f"⌛ {lesson['duration']}\n"
                f"📅 {perform_date(lesson['start_date'], lesson['time'])}\n"
                f"💶 {str(lesson['price'])}₽"
            )
            await safe_edit_text(
                event,
                text=result,
                reply_markup=generate_entity_options(
                    list_of_text=["Добавить мест", "Удалить урок", "Назад"],
                    list_of_callback=["AddLessonPlaces_", "DeleteLesson_", "AllLessonList"],
                    entity=lesson,
                    entity_key="unicode"
                )
            )


@admin_lessons.callback_query(F.data == "LessonByDirection", IsAdmin())
@inject
async def get_lesson_by_destination_start(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service],
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()
    if directions is not None:
        await safe_edit_text(
            event,
            text=f"{LESSON_LIST}\n• Выберите доступное направление",
            reply_markup=simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="AdminSearchLessonByDirection_",
                back_callback="BackToLessonMenu"
            )
        )
    else:
        await safe_edit_text(
            event,
            text="Пока нет направлений",
            reply_markup=lesson_menu()
        )


@admin_lessons.callback_query(F.data.startswith("AdminSearchLessonByDirection_"), IsAdmin())
@inject
async def get_lesson_by_destination_choice(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await state.clear()
    await safe_answer(event)
    call = event.data.partition("_")[2]
    lessons = await lesson_service.get_all_lessons_by_dest(call)

    if not lessons:
        await safe_edit_text(
            event,
            f"{LESSON_LIST}\n• Уроков по направлению {call} нет",
            reply_markup=lesson_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{LESSON_LIST}\n• Список предстоящих уроков по направлению {call}",
        reply_markup=build_lessons_pagination_keyboard(
            lessons=lessons,
            page=0,
            back_callback="BackToLessonMenu"
        )
    )


# --------------------
# UPDATE LESSON
# --------------------
class AddLessonPlaces(StatesGroup):
    places = State()


@admin_lessons.callback_query(F.data.startswith("AddLessonPlaces_"), IsAdmin())
async def add_lesson_places_start(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
    await state.update_data(code=event.data.split("_")[1])
    await safe_edit_text(
        event,
        text=f"{ADD_PLACES}\n• Введите кол-во добавляемых мест",
        reply_markup=back_to("Отмена", "AllLessonList")
    )
    await state.set_state(AddLessonPlaces.places)


@admin_lessons.message(AddLessonPlaces.places, IsAdmin())
@inject
async def add_lesson_places_places(
        event: Message,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service],
        user_service: UserService = Provide[Container.user_service]
):
    state_data = await get_and_clear(state)
    await safe_answer(event)

    add_places = await lesson_service.add_places_on_lesson(state_data['code'], int(event.text))
    if not add_places:
        await event.answer(
            text=f"{ADD_PLACES}\n• При добавлении мест что-то пошло не так",
            reply_markup=lesson_menu()
        )
        return

    users_list = await user_service.get_all_users()
    lesson: dict = await lesson_service.get_lesson_by_code(state_data['code'])
    if not users_list:
        await event.answer(
            text=f"{ADD_PLACES}\n• Места на урок успешно добавлены\n"
                 f"/// База пользователей пуста для оповещения",
            reply_markup=lesson_menu())
        return

    send, not_send = await notify_places_lesson(
        lesson=lesson,
        users_list=users_list,
        places=int(event.text)
    )

    await event.answer(
        text=f"{ADD_PLACES}\n• Места на урок успешно добавлены\n\n"
             f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
        reply_markup=lesson_menu())


# --------------------
# DELETE LESSON
# --------------------

class DeleteLesson(StatesGroup):
    lesson = State()


@admin_lessons.callback_query(F.data.startswith("DeleteLesson_"), IsAdmin())
@inject
async def delete_lesson(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service],
):
    await state.clear()
    await safe_answer(event)

    unicode = event.data.split("_")[1]
    lesson = await lesson_service.get_future_paid_lesson(unicode)

    if not lesson:
        await state.update_data(unicode=unicode)
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Желайте сделать экспорт базы данных перед удалением?",
            reply_markup=any_button_kb(
                text=["Да", "Нет", "Отмена"],
                callback=["ToRemoveLesson_yes", "ToRemoveLesson_no", "BackToAdminMenu"]
            )
        )
        return

    result = [
        f"<b>{lesson['type'].upper()}</b>\n\n"
        f"🗺 {lesson['dest']}\n"
        f"📝 {lesson['desc']}\n"
        f"👥 Осталось мест: {lesson['places']}\n"
        f"⌛ {lesson['duration']}\n"
        f"📅 {perform_date(lesson['start_date'], lesson['time'])}\n"
        f"💶 {str(lesson['price'])}₽\n"
    ]

    await safe_edit_text(
        event,
        text=f"{REMOVE}\n"
             f"• Нельзя удалить урок, который ещё не наступил и имеет хотя бы 1 участника\n\n"
             f"{'\n'.join(result)}",
        reply_markup=generate_entity_options(
            list_of_text=["Добавить мест", "Удалить урок", "Назад"],
            list_of_callback=["AddLessonPlaces_", "DeleteLesson_", "AllLessonList"],
            entity=lesson, entity_key="unicode"
        )
    )


@admin_lessons.callback_query(F.data.startswith("ToRemoveLesson_"), IsAdmin())
@inject
async def yes_to_remove_lesson(
        event: CallbackQuery,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service]
):
    await safe_answer(event)
    data = await get_and_clear(state)
    answer = event.data.split("_")[1]
    if answer == "yes":
        export = await ExportService.export_db()
        if not export:
            await safe_edit_text(
                event,
                "<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>\n\nУрок НЕ удален!\nПроизошла ошибка при экспорте данных",
                reply_markup=main_menu()
            )
            return

        await safe_delete(event)
        filename = f"backup_{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}.xlsx"
        await event.message.answer_document(
            document=BufferedInputFile(export.read(), filename=filename),
            caption="📦 Бэкап данных."
        )

    deleted = await lesson_service.delete_lesson(data['unicode'])
    if not deleted:
        if answer == 'yes':
            await event.message.answer(
                text=f"{REMOVE}\n• При удалении что-то пошло не так",
                reply_markup=lesson_menu()
            )
            return

        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• При удалении что-то пошло не так",
            reply_markup=lesson_menu()
        )
        return

    if answer == 'yes':
        await event.message.answer(
            text=f"{REMOVE}\n• Урок успешно удален!",
            reply_markup=lesson_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{REMOVE}\n• Урок успешно удален!",
        reply_markup=lesson_menu()
    )


# --------------------
# CREATE TYPE (THIS IS PART OF LESSON)
# --------------------
class AddLessonType(StatesGroup):
    type = State()


@admin_lessons.callback_query(F.data == "AddLessonType")
async def add_lesson_type(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event, state,
        text=f"{ADD_TYPE}\n• Отправьте тип урока",
        reply_markup=one_button_callback("Отмена", "BackToLessonMenu")
    )
    await state.set_state(AddLessonType.type)


@admin_lessons.message(AddLessonType.type)
@inject
async def add_lesson_type(
        event: Message,
        state: FSMContext,
        lesson_service: LessonService = Provide[Container.lesson_service],
):
    await state.clear()
    type_created = await lesson_service.add_lesson_type(event.text)
    if type_created:
        await event.answer(text=f"{ADD_TYPE}\n• Тип добавлен", reply_markup=lesson_menu())
    else:
        await event.answer(text=f"{ADD_TYPE}\n• При создании типа что-то пошло не так", reply_markup=lesson_menu())
