from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment, BufferedInputFile

from bot.config import PROVIDER_TOKEN
from bot.handlers.handler_utils import clear_and_delete, answer_and_delete
from bot.keyboards.user import *
from database import service
from utils.generate_pdf import generate_invoice_pdf_lesson
from utils.validators import is_valid_email, is_valid_phone

user_lesson = Router()

payload_lesson = {}


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
    lesson_code = event.data.split("_")[1]
    await answer_and_delete(event)

    lsn = await service.get_lesson_by_code(lesson_code)
    if lsn is None:
        await event.message.answer("Такого урока не существует")
        return
    if lsn['places'] <= 0:
        await event.message.answer("Места на урок закончились")
        return

    lesson = await service.get_user_lesson_details(event.from_user.id, lesson_code)
    if lesson is not None:
        await event.message.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование урока: {lsn['type']} | {lsn['start_date']}\n\n"
                 f"Урок уже находится в списке предстоящих Уроков.",
            reply_markup=user_main_menu().as_markup()
        )
        return

    await state.update_data(lesson=lsn)
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info['name'] is None or user_info['phone'] is None or user_info['email'] is None:
        await event.message.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование урока: {lsn['type']}\n\n"
                 f"Отправьте Ваше имя и фамилию",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
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
        text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
             f"Наименование урока: {state_data['lesson']['type']}\n\n"
             f"Отправьте Ваш email",
        reply_markup=cancel_or_back_to(
            text="Отменить бронирование",
            callback="BackToUserMainMenu"
        ).as_markup()
    )
    await state.set_state(UserBookLesson.email)


@user_lesson.message(UserBookLesson.email)
async def book_lesson(event: Message, state: FSMContext):
    state_data = await state.get_data()
    if is_valid_email(event.text):
        await state.update_data(email=event.text)
        await event.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование урока: {state_data['lesson']['type']}\n\n"
                 f"Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
        )
        await state.set_state(UserBookLesson.phone)
    else:
        await event.answer(
            text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                 f"Наименование урока: {state_data['lesson']['type']}\n\n"
                 f"EMAIL {event.text} некорректный! Попробуйте ещё раз\n\nОтправьте Ваш email",
            reply_markup=cancel_or_back_to(
                text="Отменить бронирование",
                callback="BackToUserMainMenu"
            ).as_markup()
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
                            text="При заполнении Ваших данных что-то пошло не так. Попробуйте позднее",
                            reply_markup=user_main_menu().as_markup()
                        )
                        return
            else:
                await event.answer(
                    text=f"🎫 <b>БРОНИРОВАНИЕ</b>\n"
                         f"Наименование урока: {data['lesson']['type']}\n\n"
                         f"Номер телефона {event.text} некорректный! Попробуйте ещё раз\n\n"
                         f"Отправьте Ваш номер телефона",
                    reply_markup=cancel_or_back_to(
                        text="Отменить бронирование",
                        callback="backToUserMainMenu"
                    ).as_markup()
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
        f"👥 Время начала: {lesson_info['time']}\n"
        f"👥 Продолжительность: {lesson_info['duration']}\n"
        f"📅 {lesson_info['start_date']}\n"
        f"💶 {price}\n"
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(
            text=text,
            reply_markup=confirm_booking('ApplyUserLessonBooking').as_markup()
        )
    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=confirm_booking('ApplyUserLessonBooking').as_markup()
        )
    await state.set_state(UserBookLesson.apply)


@user_lesson.callback_query(F.data == "ApplyUserLessonBooking", UserBookLesson.apply)
async def book_lesson_send_invoice(event: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    price: int = state_data['price']

    payload_lesson[event.from_user.id] = {
        "places": state_data['places'],
        "price": price,
    }

    await event.answer()
    await event.message.delete()

    prices = [LabeledPrice(label=state_data['lesson']['type'], amount=price * 100)]
    await event.bot.send_invoice(
        chat_id=event.from_user.id,
        title=state_data['lesson']['type'],
        description=state_data['desc'],
        payload=f"{state_data['lesson']['unicode']} | {event.from_user.id}",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="lesson_payment",
        need_name=True,
        need_phone_number=True,
        need_email=True
    )


@user_lesson.pre_checkout_query()
async def process_pre_checkout(event: PreCheckoutQuery):
    lesson_code = event.invoice_payload.split("|")[0].strip()
    lesson = await service.get_lesson_by_code(lesson_code)
    if not lesson or int(lesson['places']) <= 0:
        await event.answer(
            ok=False,
            error_message="❌ Места закончились(\n\nЭтот урок больше недоступен.",
        )
        await event.bot.send_message(
            chat_id=event.from_user.id,
            text="Главное меню",
            reply_markup=user_main_menu().as_markup()
        )
        return
    await event.answer(ok=True)


@user_lesson.message(F.successful_payment)
async def successful_payment(event: SuccessfulPayment):
    payment_info: SuccessfulPayment = event.successful_payment
    payload_data: str = payment_info.invoice_payload

    lesson_code: str = payload_data.split("|")[0].strip()
    places: int = int(payload_lesson[event.from_user.id]['places'])
    price: int = int(payload_lesson[event.from_user.id]['price'])

    lesson = await service.get_lesson_by_code(lesson_code)
    user_entity = await service.get_user_by_tg_id(event.from_user.id)

    paid = await service.create_surf_payment(
        tg_id=event.from_user.id, price=price, code=lesson_code
    )

    if paid:
        await service.reduce_places_on_lesson(code=lesson_code, count=places)
        result = [f"<b> 🎫 БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО 🎫</b>\n\n"
                  f"🏕 {lesson['type']}\n"
                  f"🗺 {lesson['dest']}\n"
                  f"🗺 {lesson['desc']}\n"
                  f"Время начала: {lesson['time']}\n"
                  f"Продолжительность: {lesson['duration']}\n"
                  f"📅 Даты: {lesson['start_date']}\n"
                  f"👥 Забронированных мест: {places}\n"
                  f"💶 Оплачено: {price}\n"
                  ]

        pdf = await generate_invoice_pdf_lesson(
            user_name=user_entity['name'],
            lsn_type=lesson['type'],
            destination=lesson['dest'],
            start_date=lesson['start_date'],
            time=lesson['time'],
            duration=lesson['duration'],
            places=places,
            price=price,
        )

        pdf_file = BufferedInputFile(
            pdf.getvalue(),
            filename=f"Бронирование_{lesson['type']}_{lesson['start_date']} | {user_entity['name']}.pdf"
        )

        await event.bot.send_document(chat_id=event.from_user.id, document=pdf_file)
        await event.answer(f"{'\n'.join(result)}", reply_markup=user_main_menu().as_markup())
    else:
        await event.answer(
            text=f"При сохранении оплаты что-то пошло не так, однако оплата прошла и Ваш чек доступен Вам!",
            reply_markup=user_main_menu().as_markup()
        )


# --------------------
# GETTER | UPCOMING
# --------------------
@user_lesson.callback_query(F.data == "UpcomingUserLessons")
async def upcoming_lessons_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)

    lessons = await service.get_upcoming_user_lessons(event.from_user.id)

    if lessons is not None and len(lessons) != 0:
        result = [f"<b>🔜 ВАШИ ПРЕДСТОЯЩИЕ УРОКИ 🔜</b>\n\n"]
        for i, lesson in enumerate(lessons, start=1):
            result.append(
                f"🏕 {lesson['type']}\n"
                f"🗺 {lesson['dest']}\n"
                f"🗺 Продолжительность: {lesson['duration']}\n"
                f"📅 {lesson['start_date']} | {lesson['time']}\n"
            )

        await event.message.answer(
            text=f"{'\n'.join(result)}",
            reply_markup=await generate_lesson_kb(
                lessons=lessons,
                callback="UpcomingUserLessons_",
                back_callback="UserAccount"
            )
        )
    else:
        await event.message.answer(
            text=f"<b>У Вас пока нет предстоящих туров уроков</b>",
            reply_markup=user_account_menu().as_markup()
        )


@user_lesson.callback_query(F.data.startswith("UpcomingUserLessons_"))
async def upcoming_lesson_details(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    details = await service.get_user_lesson_details(event.from_user.id, event.data.split("_")[1])

    text = (
        f"<b>🏕 {details['type']}</b>\n\n"
        f"🗺 {details['dest']}\n"
        f"🗺 {details['desc']}\n"
        f"👥 Всего забронировано мест: 1/{details['places']}\n"
        f"👥 Продолжительность: {details['duration']}\n"
        f"📅 {details['start_date']} | {details['time']}\n"
        f"💶 {details['paid']}\n"
    )

    await event.message.answer(
        text=text,
        reply_markup=cancel_or_back_to(
            text="Назад",
            callback="UpcomingUserLessons"
        ).as_markup()
    )


# --------------------
# GETTER | ALL WITH FREE PLACES
# --------------------

@user_lesson.callback_query(F.data == "AllLessonsWithFreePlaces")
async def lesson_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    lessons = await service.get_all_lessons_with_places()
    if lessons is None:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())
        return

    result = [
        "📋 <b>СПИСОК ДОСТУПНЫХ УРОКОВ:</b>\n"
        "Для подробной информации нажми на нужный урок на клавиатуре\n\n"
    ]

    for i, lesson in enumerate(lessons, start=1):
        result.append(
            f"<b>#{i}. <code>{lesson['type'].upper()}</code></b>\n"
            f"🗺 {lesson['dest']}\n"
            f"👥 Свободные места: {lesson['places']}\n"
            f"👥 Продолжительность: {lesson['duration']}\n"
            f"📅 Даты: {lesson['start_date']} | Начало: {lesson['time']}\n"
        )

    await event.message.answer(
        text=f"{'\n'.join(result)}",
        reply_markup=await generate_lesson_kb(
            lessons=lessons,
            callback="UserMoreAboutLesson_",
            back_callback="UserAccount"
        )
    )


# --------------------
# GETTER | ALL WITH FREE PLACES (MORE ABOUT)
# --------------------

@user_lesson.callback_query(F.data.startswith("UserMoreAboutLesson_"))
async def lesson_information(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split('_')[1]
    lesson = await service.get_lesson_by_code(call)
    if lesson is None:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=user_main_menu().as_markup())
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

    await event.message.answer(
        text=f"{"\n".join(result)}",
        reply_markup=await generate_keyboard2(
            list_of_text=['Забронировать урок'],
            list_of_callback=['StartBookingLesson_'],
            additional_callback=lesson['unicode']
        )
    )
