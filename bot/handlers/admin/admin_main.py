from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from bot.create import surf_bot
from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_delete
from bot.keyboards.admin import *
from database import service

admin_main = Router()

headUserMain = "<b>👨🏻‍💻 ПОЛЬЗОВАТЕЛИ\n| ГЛАВНОЕ МЕНЮ</b>"


@admin_main.message(CommandStart(), IsAdmin())
async def start(event: Message, state: FSMContext):
    await state.clear()
    await event.answer("<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>", reply_markup=main_menu().as_markup())


@admin_main.callback_query(F.data == "BackToAdminMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer("<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>", reply_markup=main_menu().as_markup())


@admin_main.callback_query(F.data == "BackToTourLessonsDirections", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer("<b>УРОКИ | ТУРЫ | НАПРАВЛЕНИЯ</b>", reply_markup=tours_lessons_directions().as_markup())


@admin_main.callback_query(F.data == "BackToUsersMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(f"{headUserMain}", reply_markup=user_menu().as_markup())


@admin_main.callback_query(F.data == "BackToTourMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text="<b>🏕 ТУРЫ | ГЛАВНОЕ МЕНЮ</b>",
        reply_markup=await tour_menu()
    )


@admin_main.callback_query(F.data == "BackToLessonMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text="<b>🏄 УРОКИ | ГЛАВНОЕ МЕНЮ</b>",
        reply_markup=await lesson_menu()
    )


@admin_main.callback_query(F.data == "BackToDirectionsMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer("<b>🗺 НАПРАВЛЕНИЯ\n| ГЛАВНОЕ МЕНЮ</b>", reply_markup=await direct_menu())


@admin_main.callback_query(F.data == "ToursLessonsDirections", IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer("<b>УРОКИ | ТУРЫ | НАПРАВЛЕНИЯ</b>",
                               reply_markup=tours_lessons_directions().as_markup())


@admin_main.callback_query(F.data.startswith('Management_'), IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)

    call = event.data.split("_")[1]
    if call == 'tour':
        await event.message.answer(
            text="<b>🏕 ТУРЫ | ГЛАВНОЕ МЕНЮ</b>",
            reply_markup=await tour_menu()
        )
    elif call == 'lesson':
        await event.message.answer(
            text="<b>🏄 УРОКИ | ГЛАВНОЕ МЕНЮ</b>",
            reply_markup=await lesson_menu()
        )
    elif call == 'direct':
        await event.message.answer(
            text="<b>🗺 НАПРАВЛЕНИЯ\n| ГЛАВНОЕ МЕНЮ</b>",
            reply_markup=await direct_menu()
        )


class Mailing(StatesGroup):
    message = State()


headerMailing = "<b>📩 РАССЫЛКА 📩</b>"


@admin_main.callback_query(F.data == "UserMailing", IsAdmin())
async def mailing(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    users = await service.get_all_users()
    if users is None:
        await event.message.answer(
            text=f"{headUserMain}\n\n• В базе нет пользователей",
            reply_markup=user_menu().as_markup()
        )
    else:
        await event.message.answer(
            text=f"{headerMailing}\n• Отправьте сообщение для рассылки",
            reply_markup=await back_to("Отмена рассылки", "BackToUsersMenu")
        )
        await state.set_state(Mailing.message)


@admin_main.message(Mailing.message, IsAdmin())
async def send_mailing(event: Message, state: FSMContext):
    mailing_message = event.message_id
    await surf_bot.copy_message(
        chat_id=event.chat.id, from_chat_id=event.chat.id,
        message_id=mailing_message, reply_markup=confirm_mailing().as_markup()
    )

    await state.update_data(msg=mailing_message)


@admin_main.callback_query(F.data == 'decline_mailing')
async def decline_mailing(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text=f"{headUserMain}\n\n• Рассылка отменена", reply_markup=user_menu().as_markup())


@admin_main.callback_query(F.data == 'send_mailing')
async def mailing_handler(event: CallbackQuery, state: FSMContext):
    errors_count = 0
    good_count = 0
    data = await state.get_data()
    await state.clear()
    await event.answer()
    mailing_message = data['msg']
    user_ids = await service.get_all_users_ids()
    if user_ids is None:
        await event.answer()
        await event.message.delete()
        await event.message.answer(
            text="\n\nУ Вас нет пользователей для рассылки сообщения",
            reply_markup=user_menu().as_markup()
        )
        return
    await event.message.delete()

    message = await event.message.answer("Рассылка начата...")
    for user_id in user_ids:
        try:
            await surf_bot.copy_message(
                chat_id=user_id,
                from_chat_id=event.from_user.id,
                message_id=mailing_message
            )
            good_count += 1
        except Exception as ex:
            errors_count += 1
            print(ex)

    await surf_bot.delete_message(chat_id=event.from_user.id, message_id=message.message_id)
    await event.message.answer(
        text=f"{headUserMain}\n\n"
             f"<b>✅ Кол-во отосланных сообщений:</b> <code>{good_count}</code>\n"
             f"<b>❌ Кол-во пользователей заблокировавших бота:</b> <code>{errors_count}</code>",
        reply_markup=user_menu().as_markup()
    )
