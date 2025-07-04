from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.simple_calendar import SimpleCalendar

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_delete, answer_and_delete, send_big_message
from bot.keyboards.admin import *
from bot.notifications.user_notification import *
from database import service
from utils.validators import is_valid_time

admin_lessons = Router()

headerAdd = "<b>🏄 ДОБАВЛЕНИЕ УРОКА 🏄</b>"
headerAddPlaces = "<b>👥 УРОК | ДОБАВЛЕНИЕ МЕСТ 👥 </b>"
headerRemove = "<b>🗑 УДАЛЕНИЕ УРОКА 🗑</b>"
headerList = "<b>📋 СПИСОК УРОКОВ 📋</b>"
headerAddType = "<b>✏️ ДОБАВЛЕНИЕ ТИПА УРОКА ✏️</b>"


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
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()
    types = await service.get_lesson_types()
    if directions is None:
        await event.message.answer(
            text=f"{headerAdd}\n• Чтобы добавить урок, должно быть хотя бы 1 направление",
            reply_markup=await lesson_menu()
        )
    elif types is None:
        await event.message.answer(
            text=f"{headerAdd}\n• Чтобы добавить урок, должно быть хотя бы 1 тип",
            reply_markup=await lesson_menu()
        )
    else:
        await event.message.answer(
            text=f"{headerAdd}\n• Выберите направление урока из доступных",
            reply_markup=await simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="SelectDestWhenAddLesson_",
                back_callback="BackToLessonMenu"
            )
        )
        await state.set_state(AddLesson.direction)


@admin_lessons.callback_query(F.data.startswith("SelectDestWhenAddLesson_"), AddLesson.direction, IsAdmin())
async def add_lesson_choice(event: CallbackQuery, state: FSMContext):
    dest = event.data.split("_")[1]
    await answer_and_delete(event)
    await state.update_data(dest=dest)

    lesson_types = await service.get_lesson_types()
    if lesson_types is None:
        await state.clear()
        await event.message.answer(
            text=f"{headerAdd}\n• Пока не существует ни одного типа урока",
            reply_markup=await lesson_menu()
        )
        return

    await event.message.answer(
        text=f"{headerAdd}Выберите тип урока",
        reply_markup=await buttons_by_entity_list_values(
            entity_list=lesson_types,
            callback="GetLessonType_",
            back_to_callback="BackToLessonMenu"
        )
    )
    await state.set_state(AddLesson.lesson_type)


@admin_lessons.callback_query(F.data.startswith("GetLessonType_"), AddLesson.lesson_type, IsAdmin())
async def add_lesson_type(event: CallbackQuery, state: FSMContext):
    less_type = event.data.split("_")[1]
    await state.update_data(type=less_type)
    await answer_and_delete(event)
    await event.message.answer(
        text=f"{headerAdd}\n• Отправьте описание урока",
        reply_markup=await back_to("Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.desc)


@admin_lessons.message(AddLesson.desc, IsAdmin())
async def add_lesson_description(event: Message, state: FSMContext):
    await state.update_data(desc=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте общее кол-во мест на урок",
        reply_markup=await back_to("Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.places)


@admin_lessons.message(AddLesson.places, IsAdmin())
async def add_lesson_places(event: Message, state: FSMContext):
    await state.update_data(places=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте дату начала урока.\n-> Для отмены нажмите команду /start",
        reply_markup=await SimpleCalendar(locale="ru_RU").start_calendar()
    )
    await state.set_state(AddLesson.start)


@admin_lessons.callback_query(SimpleCalendarCallback.filter(), AddLesson.start, IsAdmin())
async def add_lesson_date(event: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar(locale="ru_RU").process_selection(event, callback_data)
    if selected:
        await event.message.delete()
        await state.update_data(start=date)

        await event.message.answer(
            text=f"{headerAdd}\n• Отправьте время начала урока в формате: ЧЧ:MM\n<u>Пример: 10:00</u>",
            reply_markup=await back_to("Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddLesson.time)


@admin_lessons.message(AddLesson.time, IsAdmin())
async def add_lesson_time(event: Message, state: FSMContext):
    if is_valid_time(event.text):
        await state.update_data(time=event.text)
        await event.answer(
            text=f"{headerAdd}\n• Отправьте продолжительность урока в формате: Xч Y мин\n<u>Пример: 2ч 30 мин.</u>",
            reply_markup=await back_to(text="Отмена создания урока", callback="BackToLessonMenu")
        )
        await state.set_state(AddLesson.duration)
    else:
        await event.answer(
            text=f"{headerAdd}\n• Некорректный формат ввода времени. Формат должен быть ЧЧ:MM!\n"
                 f"<u>Пример: 10:00</u>\nПопробуй ещё раз: Отправь время начала урок"
        )
        await state.set_state(AddLesson.time)


@admin_lessons.message(AddLesson.duration, IsAdmin())
async def add_lesson_price(event: Message, state: FSMContext):
    await state.update_data(duration=event.text)
    await event.answer(
        text=f"{headerAdd}\n• Отправьте стоимость урока",
        reply_markup=await back_to(text="Отмена создания урока", callback="BackToLessonMenu")
    )
    await state.set_state(AddLesson.price)


@admin_lessons.message(AddLesson.price, IsAdmin())
async def add_lesson_create(event: Message, state: FSMContext):
    await state.update_data(price=event.text)
    lesson_data = await state.get_data()
    await state.clear()
    lesson = await service.create_lesson(
        desc=lesson_data['desc'],
        duration=lesson_data['duration'],
        places=lesson_data['places'],
        start=lesson_data['start'],
        time=lesson_data['time'],
        lesson_type=lesson_data['type'],
        price=lesson_data['price'],
        dest=lesson_data['dest']
    )
    if lesson[0]:
        date = lesson_data['start']
        lsn_type = lesson_data['type'].split(" ")

        lsn = (
            f"{lsn_type[0][:5]}.{lsn_type[1]} |"
            f"{DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | "
            f"{lesson_data['time']}"
        )

        await event.answer(
            text=f"{headerAdd}\n• Урок успешно добавлен!\n\n> {lsn}\n> Направление {lesson_data['dest']}",
            reply_markup=await lesson_menu()
        )
        all_users = await service.get_all_users()
        if all_users is None:
            return

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text=lsn,
                callback_data=f"UserMoreAboutLesson_{lesson[1]}"
            )
        )
        builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="UserAccount"))

        for user in all_users:
            try:
                await event.bot.send_message(
                    chat_id=int(user['tg_id']),
                    text=f"🏄 <b>ОТКРЫЛСЯ НОВЫЙ УРОК!</b> 🏄\n\n"
                         f"• {lesson_data['type']}\n"
                         f"• {lesson_data['dest']}\n"
                         f"• {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson_data['time']}\n"
                         f"⬇️ Нажми, чтобы посмотреть подробности! ⬇️",
                    reply_markup=builder.as_markup()
                )
            except Exception as e:
                print(e)
    else:
        await event.answer(
            text=f"{headerAdd}\n• При создании урока произошла ошибка",
            reply_markup=await lesson_menu()
        )


# --------------------
# GET LESSON
# --------------------
@admin_lessons.callback_query(F.data == "BookedLessons", IsAdmin())
async def get_all_booked_lessons(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    booked = await service.get_all_booked_lessons_future()
    if booked:
        result = [f"{headerList}\n• Список предстоящих забронированных уроков\n"]
        for i, lesson in enumerate(booked, start=1):
            date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")

            result.append(
                f"<b>{i}.{lesson['type']}</b>\n"
                f"📍 {lesson['dest']}\n"
                f"📅 {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}\n"
                f"💶 {lesson['price']}\n"
                f"👥 Бронь:\n{len(lesson['users']) or '—'} человек"
            )

        # Собираем весь текст
        full_text = "\n\n".join(result)

        # Отправляем частями
        await send_big_message(
            event.message,
            full_text,
            reply_markup=await lesson_menu()
        )
    else:
        await event.message.answer(
            f"{headerList}\n❌ Нет предстоящих забронированных уроков.",
            reply_markup=await lesson_menu()
        )


@admin_lessons.callback_query(F.data == "AllLessonList", IsAdmin())
async def get_all_lessons(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    lessons = await service.get_all_lessons()
    if lessons is None:
        await event.message.answer(f"{headerList}\n• Пока нет уроков", reply_markup=await lesson_menu())
        return

    page = 0
    result = [f"{headerList}\nДля подробной информации нажми на нужный урок на клавиатуре\n"]
    for i, lesson in enumerate(lessons, start=1):
        date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")
        result.append(
            f"<b>{i}.{lesson['type']}</b>\n"
            f"🗺 {lesson['dest']}\n"
            f"⌛ {lesson['duration']}\n"
            f"📅 {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}\n"
        )

    await event.message.answer(
        f"{'\n'.join(result)}",
        reply_markup=await build_lessons_pagination_keyboard(
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
    await clear_and_delete(event, state)
    data = event.data
    lessons = await service.get_all_lessons()

    if data.startswith("LessonsList_page:"):
        page = int(data.split(":")[1])
        await event.message.answer(
            f"{headerList}\n<b>• Страница {page + 1}</b>",
            reply_markup=await build_lessons_pagination_keyboard(
                lessons=lessons,
                page=page,
                back_callback="BackToLessonMenu"
            )
        )
        await event.answer()
    elif data.startswith("InfoAboutLesson_"):
        unicode = data.split("_")[1]
        lesson = await service.get_lesson_by_code(unicode)
        if lesson:
            date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")
            result = (
                f"<b>{lesson['type'].upper()}</b>\n\n"
                f"🗺 {lesson['dest']}\n"
                f"📝 {lesson['desc']}\n"
                f"👥 Осталось мест: {lesson['places']}\n"
                f"⌛ {lesson['duration']}\n"
                f"📅 {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}\n"
                f"💶 {str(lesson['price'])}₽"
            )
            await event.message.answer(
                text=result,
                reply_markup=generate_entity_options(
                    list_of_text=["Добавить мест", "Удалить урок", "Назад"],
                    list_of_callback=["AddLessonPlaces_", "DeleteLesson_", "AllLessonList"],
                    entity=lesson,
                    entity_key="unicode"
                ).as_markup()
            )

@admin_lessons.callback_query(F.data == "LessonByDirection", IsAdmin())
async def get_lesson_by_destination_start(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()
    if directions is not None:
        await event.message.answer(
            text=f"{headerList}\n• Выберите выберите доступное направление",
            reply_markup=await simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="AdminSearchLessonByDirection_",
                back_callback="BackToLessonMenu"
            )
        )
    else:
        await event.message.answer(
            text="Пока нет направлений",
            reply_markup=await lesson_menu()
        )


@admin_lessons.callback_query(F.data.startswith("AdminSearchLessonByDirection_"), IsAdmin())
async def get_lesson_by_destination_choice(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.partition("_")[2]
    lessons = await service.get_all_lessons_by_dest(call)

    if lessons:
        # Формируем строки
        lines = [
            f"{headerList}\n• Список предстоящих уроков по направлению {call}"
        ]
        for i, lesson in enumerate(lessons, start=1):
            date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")
            lines.append(
                f"<b>{i}.{lesson['type']}</b>\n"
                f"🗺 {lesson['dest']}\n"
                f"📅 {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}\n"
            )


        text = f"\n\n".join(lines)

        await send_big_message(
            message=event.message,
            text=text,
            reply_markup=await build_lessons_pagination_keyboard(
                lessons=lessons,
                back_callback="BackToLessonMenu"
            )
        )
    else:
        await event.message.answer(
            f"{headerList}\n• Уроков по направлению {call} нет",
            reply_markup=await lesson_menu()
        )


# --------------------
# UPDATE LESSON
# --------------------
class AddLessonPlaces(StatesGroup):
    places = State()


@admin_lessons.callback_query(F.data.startswith("AddLessonPlaces_"), IsAdmin())
async def add_lesson_places_start(event: CallbackQuery, state: FSMContext):
    call = event.data.split("_")[1]
    await state.update_data(code=call)
    await answer_and_delete(event)
    await event.message.answer(
        text=f"{headerAddPlaces}\n• Введите кол-во добавляемых мест",
        reply_markup=await back_to("Отмена", "LessonsList")
    )
    await state.set_state(AddLessonPlaces.places)


@admin_lessons.message(AddLessonPlaces.places, IsAdmin())
async def add_lesson_places_places(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    add_places = await service.add_places_on_lesson(state_data['code'], int(event.text))
    if add_places:
        users_list = await service.get_all_users_ids()
        if users_list is not None:
            send, not_send = await notify_about_places_lesson(state_data['code'], users_list, places=int(event.text))
            await event.answer(
                text=f"{headerAddPlaces}\n• Места на урок успешно добавлены\n\n"
                     f"<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
                reply_markup=await lesson_menu())
        else:
            await event.answer(
                text=f"{headerAddPlaces}\n• Места на урок успешно добавлены\n"
                     f"/// База пользователей пуста для оповещения",
                reply_markup=await lesson_menu())
    else:
        await event.answer(f"{headerAdd}\n• При добавлении мест что-то пошло не так", reply_markup=await lesson_menu())


# --------------------
# DELETE LESSON
# --------------------
@admin_lessons.callback_query(F.data.startswith("DeleteLesson_"), IsAdmin())
async def delete_lesson(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split("_")[1]
    lesson = await service.get_future_paid_lesson(call)
    if lesson is None:
        deleted = await service.delete_lesson(call)
        if deleted:
            await event.message.answer(
                text=f"{headerRemove}\n• Урок успешно удален!",
                reply_markup=await lesson_menu()
            )
        else:
            await event.message.answer(
                text=f"{headerRemove}\n• При удалении что-то пошло не так",
                reply_markup=await lesson_menu()
            )
    else:
        date = datetime.strptime(lesson['start_date'], "%d.%m.%Y")
        result = [
            f"<b>{lesson['type'].upper()}</b>\n\n"
            f"🗺 {lesson['dest']}\n"
            f"📝 {lesson['desc']}\n"
            f"👥 Осталось мест: {lesson['places']}\n"
            f"⌛ {lesson['duration']}\n"
            f"📅 {DAYS_RU[date.weekday()]}, {date.day} {MONTHS_RU[date.month]} | {lesson['time']}\n"
            f"💶 {str(lesson['price'])}₽\n"
        ]

        await event.message.answer(
            text=f"{headerRemove}\n"
                 f"• Нельзя удалить урок, который ещё не наступил и имеет хотя бы 1 участника\n\n"
                 f"{'\n'.join(result)}",
            reply_markup=generate_entity_options(
                list_of_text=["Добавить мест", "Удалить урок", "Назад"],
                list_of_callback=["AddLessonPlaces_", "DeleteLesson_", "AllLessonList"],
                entity=lesson, entity_key="unicode"
            ).as_markup()
        )


# --------------------
# CREATE TYPE (THIS IS PART OF LESSON)
# --------------------
class AddLessonType(StatesGroup):
    type = State()


@admin_lessons.callback_query(F.data == "AddLessonType")
async def add_lesson_type(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(f"{headerAddType}\n• Отправьте тип урока")
    await state.set_state(AddLessonType.type)


@admin_lessons.message(AddLessonType.type)
async def add_lesson_type(event: Message, state: FSMContext):
    await state.clear()
    type_created = await service.add_lesson_type(event.text)
    if type_created:
        await event.answer(
            text=f"{headerAddType}\n• Тип добавлен",
            reply_markup=await lesson_menu()
        )
    else:
        await event.answer(
            text=f"{headerAddType}\n• При создании типа что-то пошло не так",
            reply_markup=await lesson_menu()
        )
