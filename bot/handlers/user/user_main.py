from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from bot.handlers.handler_utils import clear_and_delete
from bot.keyboards.user import *
from database import service
from utils.validators import is_valid_email, is_valid_phone

user_main = Router()


# --------------------
# START
# --------------------
@user_main.message(CommandStart())
async def start(event: Message, state: FSMContext):
    await state.clear()
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info is None:
        await service.create_user(tg_id=event.from_user.id)
    await event.answer("Добро пожаловать!", reply_markup=user_main_menu().as_markup())


# --------------------
# USER ACCOUNT
# --------------------
@user_main.callback_query(F.data == "UserAccount")
async def user_account(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    user_info = await service.get_user_by_tg_id(event.from_user.id)
    if user_info is not None:
        result = [f"<b>🆔 {user_info['tg_id']}</b>\n\n"
                  f"👨🏻‍💻: {user_info['name'] if user_info['name'] is not None else "-"}\n"
                  f"📞: {user_info['phone'] if user_info['phone'] is not None else "-"}\n"
                  f"📧: {user_info['email'] if user_info['email'] is not None else "-"}\n"
                  ]
        await event.message.answer(f"{"\n".join(result)}", reply_markup=user_account_menu().as_markup())


# --------------------
# MAIN MENU
# --------------------
@user_main.callback_query(F.data == "BackToUserMainMenu")
async def back_to_menu(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer("<b>📱 Главное меню</b>", reply_markup=user_main_menu().as_markup())


# --------------------
# CHANGE DATA
# --------------------
class ChangeData(StatesGroup):
    ch_username = State()
    ch_email = State()
    ch_phone = State()


@user_main.callback_query(F.data == "UserChangeData")
async def change_data(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text="Выберите данные, которые хотите поменять",
        reply_markup=await generate_keyboard2(
            list_of_text=["Имя", "Почта", "Номер телефона"],
            list_of_callback=["Change_name", "Change_email", "Change_phone"]
        )
    )


@user_main.callback_query(F.data.startswith("Change_"))
async def select_data_to_change(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    call = event.data.split("_")[1]
    txt = "ИЗМЕНЕНИЕ ДАННЫХ\n\n"
    if call == "name":
        await event.message.answer(
            text=f"{txt}Отправьте ваше имя",
            reply_markup=cancel_or_back_to("Отменить", "userAccount").as_markup()
        )
        await state.set_state(ChangeData.ch_username)
    elif call == "email":
        await event.message.answer(
            text=f"{txt}Отправьте Вашу почту",
            reply_markup=cancel_or_back_to("Отменить", "userAccount").as_markup()
        )
        await state.set_state(ChangeData.ch_email)
    elif call == "phone":
        await event.message.answer(
            text=f"{txt}Отправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to("Отменить", "userAccount").as_markup()
        )
        await state.set_state(ChangeData.ch_phone)


@user_main.message(ChangeData.ch_username)
async def change_name(event: Message, state: FSMContext):
    await state.clear()
    updated = await service.update_user(
        event.from_user.id, name=event.text
    )
    if updated:
        await event.answer(
            text=f"Имя успешно обновлено!\nТекущее имя: {event.text}",
            reply_markup=user_account_menu().as_markup()
        )
    else:
        await event.answer(
            text="При обновлении данных что-то пошло не так",
            reply_markup=user_account_menu().as_markup()
        )


@user_main.message(ChangeData.ch_email)
async def change_email(event: Message, state: FSMContext):
    if is_valid_email(event.text):
        await state.clear()
        updated = await service.update_user(event.from_user.id, email=event.text)
        if updated:
            await event.answer(
                text=f"Почта успешно обновлена!\nТекущая почта: {event.text}",
                reply_markup=user_account_menu().as_markup()
            )
        else:
            await event.answer(
                text="При обновлении данных что-то пошло не так",
                reply_markup=user_account_menu().as_markup()
            )
    else:
        txt = "ИЗМЕНЕНИЕ ДАННЫХ\n\n"
        await event.answer(
            text=f"{txt}Почта {event.text} некорректная. Попробуйте ещё раз\n\nОтправьте Вашу почту",
            reply_markup=cancel_or_back_to("Отменить", "userAccount").as_markup()
        )
        await state.set_state(ChangeData.ch_email)


@user_main.message(ChangeData.ch_phone)
async def change_phone(event: Message, state: FSMContext):
    if is_valid_phone(event.text):
        await state.clear()
        updated = await service.update_user(event.from_user.id, phone=event.text)
        if updated:
            await event.answer(
                text=f"Номер телефона успешно обновлен!\nТекущий номер: {event.text}",
                reply_markup=user_account_menu().as_markup()
            )
        else:
            await event.answer(
                text="При обновлении данных что-то пошло не так",
                reply_markup=user_account_menu().as_markup()
            )
    else:
        txt = "ИЗМЕНЕНИЕ ДАННЫХ\n\n"
        await event.answer(
            text=f"{txt}Номер {event.text} некорректный. Попробуйте ещё раз\n\nОтправьте Ваш номер телефона",
            reply_markup=cancel_or_back_to("Отменить", "userAccount").as_markup()
        )
        await state.set_state(ChangeData.ch_email)
