from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice

from bot.config import PROVIDER_TOKEN
from bot.create import payment_payload
from bot.handlers.handler_utils import send_by_instance, safe_answer, safe_delete, edit_and_answer, safe_edit_text, \
    get_and_clear
from bot.keyboards.user import *
from database import service
from utils.validators import is_valid_email, is_valid_phone

user_lesson = Router()


# --------------------
# BOOKING
# --------------------
class UserBookLesson(StatesGroup):
    lesson = State()
    username = State()
    phone = State()
    email = State()
    exists = State()
    apply = State()


@user_lesson.callback_query(F.data.startswith("StartBookingLesson_"))
async def book_lesson(event: CallbackQuery, state: FSMContext):
    await state.clear()
    lesson_code = event.data.split("_")[1]

    lsn = await service.get_lesson_by_code(lesson_code)
    if lsn is None:
        await edit_and_answer(event, "❌ <b>Такого урока не существует</b>", user_main_menu())
        return
    if lsn['places'] <= 0:
        await edit_and_answer(event, "<b>⛔️ Места на урок закончились ⛔️</b>", user_main_menu())
        return

    lesson = await service.get_user_lesson_details(event.from_user.id, lesson_code)
    lesson_naming = (
        f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
        f"Наименование урока:\n{lsn['type']} | {lsn['start_date']} | {lsn['type']}"
    )
    if lesson is not None:
        await edit_and_answer(
            event,
            text=f"{lesson_naming}\n\n❗️ <b>Урок уже находится в списке предстоящих уроков</b>",
            reply_markup=user_main_menu()
        )
        return

    await state.update_data(lesson=lsn, lsn_naming=lesson_naming)
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info['name'] is None or user_info['phone'] is None or user_info['email'] is None:
        await edit_and_answer(
            event,
            text=f"{lesson_naming}\n\n🙋🏻 Отправьте Ваше имя и фамилию",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
        )
        await state.set_state(UserBookLesson.username)
    else:
        await state.set_state(UserBookLesson.exists)
        await book_lesson_applying(event, state)


@user_lesson.message(UserBookLesson.username)
async def book_lesson(event: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.update_data(name=event.text)
    await event.answer(
        text=f"{state_data['lsn_naming']}\n\n📩 Отправьте Ваш email",
        reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
    )
    await state.set_state(UserBookLesson.email)


@user_lesson.message(UserBookLesson.email)
async def book_lesson(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_email(event.text):
        await state.update_data(email=event.text)
        await event.answer(
            text=f"{state_data['lsn_naming']}\n\n📞 Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
        )
        await state.set_state(UserBookLesson.phone)
    else:
        await event.answer(
            text=f"{state_data['lsn_naming']}\n\n"
                 f"EMAIL <b>{event.text}</b> некорректный! Попробуйте ещё раз\n\n📩 Отправьте Ваш email",
            reply_markup=cancel_or_back_to(text="✖️ Отменить бронирование", callback="BackToUserMainMenu")
        )
        await state.set_state(UserBookLesson.email)


@user_lesson.message(StateFilter(UserBookLesson.phone, UserBookLesson.exists))
async def book_lesson_applying(event: Message | CallbackQuery, state: FSMContext):
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
                            text=f"{data['lsn_naming']}\n\n⛔️ При заполнении Ваших данных что-то пошло не так. Попробуйте позднее",
                            reply_markup=user_main_menu()
                        )
                        return
            else:
                await event.answer(
                    text=f"{data['lsn_naming']}"
                         f"Номер телефона <b>{event.text}</b> некорректный! Попробуйте ещё раз\n\n"
                         f"📞 Отправьте Ваш номер телефона",
                    reply_markup=cancel_or_back_to(
                        text="✖️ Отменить бронирование",
                        callback="backToUserMainMenu")
                )
                await state.set_state(UserBookLesson.phone)
                return

    book_places = 1
    lesson_info = await service.get_lesson_by_code(data['lesson']['unicode'])

    price = lesson_info['price'] * book_places
    await state.update_data(price=price)
    await state.update_data(places=book_places)
    await state.update_data(desc=lesson_info['desc'])
    user_entity = await service.get_user_by_tg_id(event.from_user.id)

    text = (
        f"🎫 <b>ПОДТВЕРДЖЕНИЕ БРОНИРОВАНИЯ</b> 🎫\n\n"
        f"Участник:\n"
        f"🙋🏻 {user_entity['name']}\n\n"
        f"🗺 {lesson_info['dest']}\n"
        f"📝 {lesson_info['desc']}\n"
        f"👥 Кол-во бронируемых мест: {book_places}\n"
        f"⏰ Время начала: {lesson_info['time']}\n"
        f"⌛️ Продолжительность: {lesson_info['duration']}\n"
        f"📅 Дата {lesson_info['start_date']}\n"
        f"💶 {price}\n"
    )
    await send_by_instance(
        event=event,
        text=text,
        reply_markup=confirm_booking('ApplyUserLessonBooking')
    )
    await state.set_state(UserBookLesson.apply)


@user_lesson.callback_query(F.data == "ApplyUserLessonBooking", UserBookLesson.apply)
async def book_lesson_send_invoice(event: CallbackQuery, state: FSMContext):
    state_data = await get_and_clear(state)

    price: int = state_data['price']
    payment_payload[event.from_user.id] = {
        "lesson": {
            "places": state_data['places'],
            "price": price,
            "unicode": state_data['lesson']['unicode']
        }
    }

    await safe_answer(event)
    await safe_delete(event)

    prices = [LabeledPrice(label=state_data['lesson']['type'], amount=price * 100)]
    await event.bot.send_invoice(
        chat_id=event.from_user.id,
        title=state_data['lesson']['type'],
        description=state_data['desc'],
        payload=f"event: {event.data}",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="lesson_payment",
        need_name=True,
        need_phone_number=True,
        need_email=True
    )


# --------------------
# GETTER | UPCOMING
# --------------------
@user_lesson.callback_query(F.data == "UpcomingUserLessons")
async def upcoming_lessons_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    lessons = await service.get_upcoming_user_lessons(event.from_user.id)

    if not lessons:
        await safe_edit_text(
            event,
            text=f"<b>✖️🏄 У Вас пока нет предстоящих туров уроков</b>",
            reply_markup=user_account_menu()
        )
        return

    result = [f"<b>🏄🔜 ВАШИ ПРЕДСТОЯЩИЕ УРОКИ</b>\n\n"]
    # for i, lesson in enumerate(lessons, start=1):
    #     result.append(
    #         f"🏕 {lesson['type']}\n"
    #         f"🗺 {lesson['dest']}\n"
    #         f"🗺 Продолжительность: {lesson['duration']}\n"
    #         f"📅 {lesson['start_date']} | {lesson['time']}\n"
    #     )

    await safe_edit_text(
        event=event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_upcoming_lessons_pagination_keyboard(
            lessons=lessons,
            callback="UpcomingUserLessons_",
            back_callback="UserAccount"

        )
    )


@user_lesson.callback_query(lambda c: (
        c.data.startswith("UpcomingUserList_page:") or
        c.data.startswith("UpcomingUserLessons_")
))
async def upcoming_lesson_details(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    if event.data.startswith("UpcomingUserList_page:"):
        lessons = await service.get_upcoming_user_lessons(event.from_user.id)
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"<b>🏄🔜 ВАШИ ПРЕДСТОЯЩИЕ УРОКИ</b>\n• Страница {page + 1}",
            reply_markup=build_upcoming_lessons_pagination_keyboard(
                lessons=lessons,
                page=page,
                back_callback="UserAccount"
            )
        )
        return

    details = await service.get_user_lesson_details(event.from_user.id, event.data.split("_")[1])
    text = (
        f"<b>🏄 {details['type']}</b>\n\n"
        f"🗺 {details['dest']}\n"
        f"✏️ {details['desc']}\n"
        f"👥 Забронировано мест: 1/{details['places']}\n"
        f"⌛️ Продолжительность: {details['duration']}\n"
        f"📅 {details['start_date']} | {details['time']}\n"
        f"💶 {details['paid']}\n"
    )

    await safe_edit_text(
        event,
        text=text,
        reply_markup=cancel_or_back_to(
            text="🔙 Назад",
            callback="UpcomingUserLessons"
        )
    )


# --------------------
# GETTER | ALL WITH FREE PLACES
# --------------------

@user_lesson.callback_query(F.data == "AllLessonsWithFreePlaces")
async def lesson_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    lessons = await service.get_all_lessons_with_places()
    if lessons is None:
        await edit_and_answer(event, f"<b>✖️🏄 Пока нет уроков</b>", reply_markup=user_main_menu())
        return

    result = [
        "🏄 <b>СПИСОК ДОСТУПНЫХ УРОКОВ</b> 🏄\n"
        "• Для подробной информации нажми на нужный урок на клавиатуре\n\n"
    ]

    # for i, lesson in enumerate(lessons, start=1):
    #     result.append(
    #         f"<b>#{i}. <code>{lesson['type'].upper()}</code></b>\n"
    #         f"🗺 {lesson['dest']}\n"
    #         f"👥 Свободные места: {lesson['places']}\n"
    #         f"👥 Продолжительность: {lesson['duration']}\n"
    #         f"📅 Даты: {lesson['start_date']} | Начало: {lesson['time']}\n"
    #     )

    await safe_edit_text(
        event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_lessons_pagination_keyboard(
            lessons=lessons,
            callback="UserMoreAboutLesson_",
            back_callback="BackToUserMainMenu"
        )
    )


# --------------------
# GETTER | ALL WITH FREE PLACES (MORE ABOUT)
# --------------------
@user_lesson.callback_query(lambda c: (
        c.data.startswith("AllToursUserList_page:") or
        c.data.startswith("UserMoreAboutLesson_")
))
async def lesson_information(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    if event.data.startswith("AllToursUserList_page:"):
        lessons = await service.get_all_lessons_with_places()
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"🏄 <b>СПИСОК ДОСТУПНЫХ УРОКОВ</b> 🏄\n• Страница {page + 1}",
            reply_markup=build_lessons_pagination_keyboard(
                lessons=lessons,
                page=page,
                back_callback="BackToUserMainMenu"
            )
        )
        return

    call = event.data.split('_')[1]
    lesson = await service.get_lesson_by_code(call)
    if lesson is None:
        await event.message.answer(f"<b>✖️🏕 Пока нет уроков</b>", reply_markup=user_main_menu())
        return

    result = [
        f"<b>🏕 {lesson['type'].upper()}</b>\n\n"
        f"🗺 {lesson['dest']}\n"
        f"📝 {lesson['desc']}\n"
        f"👥 Свободные места: {lesson['places']}\n"
        f"👥 Время начала: {lesson['time']}\n"
        f"👥 Продолжительность: {lesson['duration']}\n"
        f"📅 {lesson['start_date']}\n"
        f"💶 {lesson['price']}₽\n"
    ]

    await safe_edit_text(
        event,
        text=f"{"\n".join(result)}",
        reply_markup=generate_keyboard(
            text='Забронировать урок',
            callback='StartBookingLesson_',
            value_key=lesson['unicode'],
            back_callback="BackToUserMainMenu"
        )
    )
