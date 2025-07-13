from aiogram import Router, F
from bot.keyboards.admin import *
from bot.handlers.handler_utils import *
from bot.filters.isAdmin import IsAdmin
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dependency_injector.wiring import Provide, inject
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from DIcontainer import Container

from service.export_service import ExportService
from service.user_service import UserService
from utils.set_commands import set_admin_commands
from bot.notifications.user_notification import mailing_action

admin_main = Router()

headUserMain = "<b>👨🏻‍💻 ПОЛЬЗОВАТЕЛИ\n| ГЛАВНОЕ МЕНЮ</b>"


@admin_main.message(F.text.in_(['/admin', '/start']), IsAdmin())
async def start(event: Message, state: FSMContext):
    await state.clear()
    await set_admin_commands(surf_bot)
    await event.answer("<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>", reply_markup=main_menu())


@admin_main.callback_query(F.data == "BackToAdminMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    await safe_edit_text(event, "<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>", reply_markup=main_menu())


@admin_main.callback_query(F.data == "BackToTourLessonsDirections", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event, state,
        "<b>УРОКИ | ТУРЫ | НАПРАВЛЕНИЯ</b>",
        reply_markup=tours_lessons_directions()
    )


@admin_main.callback_query(F.data == "DatabaseExport")
async def export_db(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    await safe_delete(event)

    export = await ExportService.export_db()
    if not export:
        await safe_edit_text(
            event,
            "<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>\n\nПроизошла ошибка при экспорте данных",
            reply_markup=main_menu()
        )
        return
    filename = f"backup_{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}.xlsx"
    await event.message.answer_document(
        document=BufferedInputFile(export.read(), filename=filename),
        caption="📦 Бэкап данных."
    )
    await event.message.answer("<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>", reply_markup=main_menu())


@admin_main.callback_query(F.data == "BackToUsersMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, f"{headUserMain}", reply_markup=user_menu())


@admin_main.callback_query(F.data == "BackToTourMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, text="<b>🏕 ТУРЫ | ГЛАВНОЕ МЕНЮ</b>", reply_markup=tour_menu())


@admin_main.callback_query(F.data == "BackToLessonMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, text="<b>🏄 УРОКИ | ГЛАВНОЕ МЕНЮ</b>", reply_markup=lesson_menu())


@admin_main.callback_query(F.data == "BackToDirectionsMenu", IsAdmin())
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    await safe_edit_text(event, "<b>🗺 НАПРАВЛЕНИЯ\n| ГЛАВНОЕ МЕНЮ</b>", reply_markup=direct_menu())


@admin_main.callback_query(F.data == "ToursLessonsDirections", IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event, state,
        "<b>УРОКИ | ТУРЫ | НАПРАВЛЕНИЯ</b>",
        reply_markup=tours_lessons_directions()
    )


@admin_main.callback_query(F.data.startswith('Management_'), IsAdmin())
async def tours_and_directions(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    call = event.data.split("_")[1]
    if call == 'tour':
        await safe_edit_text(event,
                             text="<b>🏕 ТУРЫ | ГЛАВНОЕ МЕНЮ</b>",
                             reply_markup=tour_menu()
                             )
    elif call == 'lesson':
        await safe_edit_text(event,
                             text="<b>🏄 УРОКИ | ГЛАВНОЕ МЕНЮ</b>",
                             reply_markup=lesson_menu()
                             )
    elif call == 'direct':
        await safe_edit_text(event,
                             text="<b>🗺 НАПРАВЛЕНИЯ\n| ГЛАВНОЕ МЕНЮ</b>",
                             reply_markup=direct_menu()
                             )


class Mailing(StatesGroup):
    message = State()


headerMailing = "<b>📩 РАССЫЛКА 📩</b>"


@admin_main.callback_query(F.data == "UserMailing", IsAdmin())
@inject
async def mailing(
        event: CallbackQuery,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    await state.clear()
    await safe_answer(event)

    users = await user_service.get_all_users()
    if not users:
        await safe_edit_text(
            event,
            text=f"{headUserMain}\n\n• В базе нет пользователей",
            reply_markup=user_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{headerMailing}\n• Отправьте сообщение для рассылки",
        reply_markup=back_to("Отмена рассылки", "BackToUsersMenu")
    )
    await state.set_state(Mailing.message)


@admin_main.message(Mailing.message, IsAdmin())
async def send_mailing(event: Message, state: FSMContext):
    mailing_message = event.message_id
    await surf_bot.copy_message(
        chat_id=event.chat.id, from_chat_id=event.chat.id,
        message_id=mailing_message, reply_markup=confirm_mailing()
    )

    await state.update_data(msg=mailing_message)


@admin_main.callback_query(F.data == 'decline_mailing')
async def decline_mailing(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, text=f"{headUserMain}\n• Рассылка отменена", reply_markup=user_menu())


@admin_main.callback_query(F.data == 'send_mailing')
@inject
async def mailing_handler(
        event: CallbackQuery,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    data = await get_and_clear(state)
    await safe_answer(event)

    mailing_message = data['msg']
    user_ids = await user_service.get_all_users_ids()
    if not user_ids:
        await safe_edit_text(
            event,
            text=f"{headerMailing}\n• У Вас нет пользователей для рассылки сообщения",
            reply_markup=user_menu()
        )
        return

    await safe_edit_text(event, "Рассылка начата...")
    send, not_send = await mailing_action(
        from_chat=event.from_user.id,
        message=mailing_message,
        users=user_ids
    )

    await safe_edit_text(
        event,
        text=f"{headUserMain}\n\n<b>Уведомление</b>\n✅ Получили: {send}\n❌ Не получили: {not_send}",
        reply_markup=user_menu()
    )
