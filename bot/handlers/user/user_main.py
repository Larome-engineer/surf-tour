from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from dependency_injector.wiring import Provide, inject

from bot.config import NOTIFICATION_CHAT
from bot.create import payment_payload
from utils.DIcontainer import Container
from bot.handlers.handler_utils import *
from bot.keyboards.user import *
from service.user_service import UserService
from utils.set_commands import set_user_commands
from utils.validators import is_valid_email, is_valid_phone

user_main = Router()

logger_user = logging.getLogger(__name__)

HELLO_MSG = "<b>🏠 ГЛАВНОЕ МЕНЮ</b>"
DATA_CHANGE = "<b>♻️ ИЗМЕНЕНИЕ ДАННЫХ</b>"
MAIN_MENU = "<b>🏠 ГЛАВНОЕ МЕНЮ</b>"

''' USER START COMMAND '''


@user_main.message(CommandStart())
@inject
async def start(
        event: Message,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    await state.clear()
    try:
        payment_payload.pop(event.from_user.id)
    except Exception as e:
        logger_user.error(e)
        pass
    user_info = await user_service.get_user_by_tg_id(event.from_user.id)
    if user_info is None:
        await user_service.create_user(tg_id=event.from_user.id)
        await safe_send(
            text=f"Новый пользователь зашел в бота! 🙋🏻✅\n🆔 {event.from_user.id}",
            chat_id=NOTIFICATION_CHAT
        )
    await set_user_commands(surf_bot, event.from_user.id)
    await event.answer(HELLO_MSG, reply_markup=user_main_menu())


@user_main.callback_query(F.data == "DisableNotifications")
@inject
async def disable_notifications(
        event: CallbackQuery,
        user_service: UserService = Provide[Container.user_service]
):
    await safe_answer(event)
    disabled = await user_service.disable_notifications(event.from_user.id)
    if disabled:
        await safe_edit_text(event, text="✖️📨 <b>Уведомления отключены!</b>")
    else:
        await safe_edit_text(
            event,
            text="✖️ При отключении уведомлений что-то пошло не так...\n\nПопробуйте в другой раз"
        )


''' USER ACCOUNT MENU '''


@user_main.callback_query(F.data == "UserAccount")
@inject
async def user_account(
        event: CallbackQuery,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    await safe_answer(event)
    await state.clear()
    user_info = await user_service.get_user_by_tg_id(event.from_user.id)
    if user_info is not None:
        result = [
            f"<b>🆔 {user_info['tg_id']}</b>\n\n"
            f"👨🏻‍💻: {user_info['name'] if user_info['name'] is not None else "-"}\n"
            f"📞: {user_info['phone'] if user_info['phone'] is not None else "-"}\n"
            f"📧: {user_info['email'] if user_info['email'] is not None else "-"}\n"
        ]

        text = "\n".join(result)
        await safe_edit_text(
            event=event,
            text=f"{text}",
            reply_markup=user_account_menu()
        )


''' BACK TO MAIN MENU'''


@user_main.callback_query(F.data == "BackToUserMainMenu")
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    await safe_edit_text(
        event,
        text=MAIN_MENU,
        reply_markup=user_main_menu()
    )


'''CHANGE USER DATA'''


class ChangeData(StatesGroup):
    ch_username = State()
    ch_email = State()
    ch_phone = State()


@user_main.callback_query(F.data == "UserChangeData")
async def change_data(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event=event,
        state=state,
        text=f"{DATA_CHANGE}\n• Выберите параметр, который хотите поменять",
        reply_markup=generate_keyboard2(
            list_of_text=["🪪 Имя и фамилия", "✉️ Почта", "📞 Номер телефона"],
            list_of_callback=["Change_name", "Change_email", "Change_phone"]
        )
    )


@user_main.callback_query(F.data.startswith("Change_"))
async def select_data_to_change(event: CallbackQuery, state: FSMContext):
    call = event.data.split("_")[1]
    option_map = {
        "name": [f"{DATA_CHANGE}\n• Отправьте ваше имя и фамилию", ChangeData.ch_username],
        "email": [f"{DATA_CHANGE}\n• Отправьте Вашу почту", ChangeData.ch_email],
        "phone": [f"{DATA_CHANGE}\n• Отправьте Ваш номер телефона", ChangeData.ch_phone]
    }
    await clear_and_edit(
        event, state,
        text=option_map[call][0],
        reply_markup=cancel_or_back_to("✖️ Отменить", "UserAccount")
    )
    await state.set_state(option_map[call][1])


@user_main.message(ChangeData.ch_username)
@inject
async def change_name(
        event: Message,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    await state.clear()
    updated = await user_service.update_user(event.from_user.id, name=event.text)
    if not updated:
        await event.answer(
            text=f"{DATA_CHANGE}\n• ❌ При обновлении данных что-то пошло не так",
            reply_markup=user_account_menu()
        )
        return

    await event.answer(
        text=f"{DATA_CHANGE}\n• Имя успешно обновлено ✅\n\nТекущее имя: {event.text}",
        reply_markup=user_account_menu()
    )


@user_main.message(ChangeData.ch_email)
@inject
async def change_email(
        event: Message,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    if is_valid_email(event.text):
        await state.clear()
        updated = await user_service.update_user(event.from_user.id, email=event.text)
        if not updated:
            await event.answer(
                text=f"{DATA_CHANGE}\n• ❌ При обновлении данных что-то пошло не так",
                reply_markup=user_account_menu()
            )
            return
        await event.answer(
            text=f"{DATA_CHANGE}\n• Почта успешно обновлена ✅\n\nТекущая почта: {event.text}",
            reply_markup=user_account_menu()
        )
    else:
        await event.answer(
            text=f"{DATA_CHANGE}\n\nПочта <b>{event.text}</b> некорректная. Попробуйте ещё раз\n\n• Отправьте Вашу почту",
            reply_markup=cancel_or_back_to("✖️ Отменить", "userAccount")
        )
        await state.set_state(ChangeData.ch_email)


@user_main.message(ChangeData.ch_phone)
@inject
async def change_phone(
        event: Message,
        state: FSMContext,
        user_service: UserService = Provide[Container.user_service]
):
    if is_valid_phone(event.text):
        await state.clear()
        updated = await user_service.update_user(event.from_user.id, phone=event.text)
        if not updated:
            await event.answer(
                text=f"{DATA_CHANGE}\n• ❌ При обновлении данных что-то пошло не так",
                reply_markup=user_account_menu()
            )
            return
        await event.answer(
            text=f"{DATA_CHANGE}\n• Номер телефона успешно обновлен ✅\n\nТекущий номер: {event.text}",
            reply_markup=user_account_menu()
        )

    else:
        await event.answer(
            text=f"{DATA_CHANGE}\n\nНомер <b>{event.text}</b> некорректный. Попробуйте ещё раз\n\n• Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to("Отменить", "userAccount")
        )
        await state.set_state(ChangeData.ch_email)
