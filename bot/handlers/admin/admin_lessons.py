from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.simple_calendar import SimpleCalendar

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import edit_and_answer, get_and_clear, safe_edit_text, \
    safe_answer, clear_and_edit, safe_delete
from bot.keyboards.admin import *
from bot.notifications.user_notification import *
from database import service
from utils.validators import is_valid_time

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
async def add_lesson_start(event: CallbackQuery, state: FSMContext):
    await state.clear()
    directions = await service.get_all_destinations()
    types = await service.get_lesson_types()
    if directions is None or types is None:
        await edit_and_answer(
            event,
            text=f"{ADD_LESSON}\n• Чтобы добавить урок/тур, должно быть хотя бы 1 направление",
            reply_markup=lesson_menu()
        )

    else:
        await edit_and_answer(
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
async def add_lesson_choice(event: CallbackQuery, state: FSMContext):
    await state.update_data(dest=event.data.split("_")[1])

    lesson_types = await service.get_lesson_types()
    if lesson_types is None:
        await state.clear()
        await edit_and_answer(
            event,
            text=f"{ADD_LESSON}\n• Пока не существует ни одного типа урока",
            reply_markup=lesson_menu()
        )
        return

    await edit_and_answer(
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
    await state.update_data(type=event.data.split("_")[1])
    await edit_and_answer(
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
    await state.update_data(places=event.text)
    await event.answer(
        text=f"{ADD_LESSON}\n• Отправьте дату начала урока.\n-> Для отмены нажмите команду /start",
        reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
    )
    await state.set_state(AddLesson.start)


@admin_lessons.callback_query(SimpleCalendarCallback.filter(), AddLesson.start, IsAdmin())
async def add_lesson_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        await state.update_data(start=date)

        await edit_and_answer(
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
async def add_lesson_create(event: Message, state: FSMContext):
    lesson_data = await get_and_clear(state)

    lesson = await service.create_lesson(
        desc=lesson_data['desc'],
        duration=lesson_data['duration'],
        places=lesson_data['places'],
        start=lesson_data['start'],
        time=lesson_data['time'],
        lesson_type=lesson_data['type'],
        price=event.text,
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
        lesson_data['type'],
        lesson_data['start'],
        lesson_data['time']
    )

    all_users = await service.get_all_users()
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
async def get_all_booked_lessons(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    booked = await service.get_all_booked_lessons_future()
    if not booked:
        await edit_and_answer(
            event,
            f"{LESSON_LIST}\n❌ Нет предстоящих забронированных уроков.",
            reply_markup=lesson_menu()
        )
        return

    result = [
        f"{LESSON_LIST}\n• Список предстоящих забронированных уроков\n"
    ]

    # for i, lesson in enumerate(booked, start=1):
    #     result.append(
    #         f"<b>{i}.{lesson['type']}</b>\n"
    #         f"📍 {lesson['dest']}\n"
    #         f"📅 {perform_date(lesson['start_date'], lesson['time'])}\n"
    #         f"💶 {lesson['price']}\n"
    #         f"👥 Бронь:\n{len(lesson['users']) or '—'} человек"
    #     )
    #
    # # Собираем весь текст
    # full_text = "\n\n".join(result)

    # Отправляем частями
    await safe_edit_text(
        event,
        text="\n\n".join(result),
        reply_markup=build_lessons_pagination_keyboard(
            lessons=booked,
            page=0,
            back_callback="BackToLessonMenu"
        )
    )


@admin_lessons.callback_query(F.data == "AllLessonList", IsAdmin())
async def get_all_lessons(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    lessons = await service.get_all_lessons()
    if not lessons:
        await edit_and_answer(event, f"{LESSON_LIST}\n• Пока нет уроков", reply_markup=lesson_menu())
        return

    page = 0
    result = [
        f"{LESSON_LIST}\nДля подробной информации нажми на нужный урок на клавиатуре\n"
    ]
    # for i, lesson in enumerate(lessons, start=1):
    #     result.append(
    #         f"<b>{i}.{lesson['type']}</b>\n"
    #         f"🗺 {lesson['dest']}\n"
    #         f"⌛ {lesson['duration']}\n"
    #         f"📅 {perform_date(lesson['start_date'], lesson['time'])}\n"
    #     )

    await safe_edit_text(
        event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_lessons_pagination_keyboard(
            lessons=lessons,
            page=page,
            back_callback="BackToLessonMenu"
        )
    )


# @admin_lessons.callback_query(F.data.startswith("InfoAboutLesson_"), IsAdmin())
@admin_lessons.callback_query(lambda c: (
        c.data.startswith("LessonsList_page:") or
        c.data.startswith("InfoAboutLesson_")
), IsAdmin())
async def get_lesson_by_code(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    data = event.data
    lessons = await service.get_all_lessons()

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
        lesson = await service.get_lesson_by_code(data.split("_")[1])
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
async def get_lesson_by_destination_start(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    directions = await service.get_all_destinations()
    if directions is not None:
        await safe_edit_text(
            event,
            text=f"{LESSON_LIST}\n• Выберите выберите доступное направление",
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
async def get_lesson_by_destination_choice(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    call = event.data.partition("_")[2]
    lessons = await service.get_all_lessons_by_dest(call)

    if not lessons:
        await safe_edit_text(
            event,
            f"{LESSON_LIST}\n• Уроков по направлению {call} нет",
            reply_markup=lesson_menu()
        )
        return

    lines = [
        f"{LESSON_LIST}\n• Список предстоящих уроков по направлению {call}"
    ]
    # for i, lesson in enumerate(lessons, start=1):
    #     lines.append(
    #         f"<b>{i}.{lesson['type']}</b>\n"
    #         f"🗺 {lesson['dest']}\n"
    #         f"📅 {perform_date(lesson['start_date'], lesson['time'])}\n"
    #     )
    #
    # text = f"\n\n".join(lines)

    await safe_edit_text(
        event,
        text=f"\n\n".join(lines),
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
    await state.update_data(code=event.data.split("_")[1])
    await edit_and_answer(
        event,
        text=f"{ADD_PLACES}\n• Введите кол-во добавляемых мест",
        reply_markup=back_to("Отмена", "LessonsList")
    )
    await state.set_state(AddLessonPlaces.places)


@admin_lessons.message(AddLessonPlaces.places, IsAdmin())
async def add_lesson_places_places(event: Message, state: FSMContext):
    state_data = await get_and_clear(state)
    await safe_answer(event)

    add_places = await service.add_places_on_lesson(state_data['code'], int(event.text))
    if not add_places:
        await event.answer(
            text=f"{ADD_PLACES}\n• При добавлении мест что-то пошло не так",
            reply_markup=lesson_menu()
        )
        return

    users_list = await service.get_all_users()
    if not users_list:
        await event.answer(
            text=f"{ADD_PLACES}\n• Места на урок успешно добавлены\n"
                 f"/// База пользователей пуста для оповещения",
            reply_markup=lesson_menu())
        return

    send, not_send = await notify_places_lesson(
        lesson_code=state_data['code'],
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
async def delete_lesson(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    unicode = event.data.split("_")[1]
    lesson = await service.get_future_paid_lesson(unicode)

    if not lesson:
        await state.update_data(unicode=unicode)
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Желайте сделать экспорт базы данных перед удалением?",
            reply_markup=any_button_kb(
                text=["Да", "Нет"],
                callback=["ToRemoveLesson_yes", "ToRemoveLesson_no"]
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
async def yes_to_remove_lesson(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
    data = await get_and_clear(state)
    answer = event.data.split("_")[1]
    if answer == "yes":
        export = await service.export_db()
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

    deleted = await service.delete_lesson(data['unicode'])
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
    await clear_and_edit(event, state, f"{ADD_TYPE}\n• Отправьте тип урока")
    await state.set_state(AddLessonType.type)


@admin_lessons.message(AddLessonType.type)
async def add_lesson_type(event: Message, state: FSMContext):
    await state.clear()
    type_created = await service.add_lesson_type(event.text)
    if type_created:
        await event.answer(text=f"{ADD_TYPE}\n• Тип добавлен", reply_markup=lesson_menu())
    else:
        await event.answer(text=f"{ADD_TYPE}\n• При создании типа что-то пошло не так", reply_markup=lesson_menu())
