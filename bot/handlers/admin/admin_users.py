from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_delete
from bot.keyboards.admin import *
from database import service

admin_users = Router()

headerChange = "<b>ПОИСК ПОЛЬЗОВАТЕЛЯ</b>"
headerList = "<b>📋 СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ 📋</b>"
headerSearch = "<b>🔎 ПОИСК ПОЛЬЗОВАТЕЛЯ 🔎</b>"
headUsersMain = "<b>👨🏻‍💻 ПОЛЬЗОВАТЕЛИ\n| ГЛАВНОЕ МЕНЮ</b>"


####### USERS #######
@admin_users.callback_query(F.data == "Users", IsAdmin())
async def users(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(f"{headUsersMain}", reply_markup=user_menu().as_markup())


@admin_users.callback_query(F.data == "UsersList", IsAdmin())
async def get_all_users(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)

    user_list = await service.get_all_users()
    if user_list is not None:
        result = [f"{headerList}\n"]
        for i, user in enumerate(user_list, start=1):
            result.append(
                f"<b>#{i}. {user['name'] if user['name'] is not None else "Нет имени"}</b>\n"
                f"🔜<code>{user['tg_id']}</code>\n"
                f"📝 {user['phone'] if user['phone'] is not None else "Нет номера"}\n"
                f"👥 {user['email'] if user['email'] is not None else "Нет почты"}\n"
            )
        await event.message.answer(f"{'\n'.join(result)}", reply_markup=user_menu().as_markup())
    else:
        await event.message.answer(f"{headUsersMain}\n\n• В базе пока нет пользователей",
                                   reply_markup=user_menu().as_markup())


@admin_users.callback_query(F.data == "UsersInfo", IsAdmin())
async def user_get_info(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(f"{headerSearch}\n• Выбери опцию поиска", reply_markup=user_info().as_markup())


class SearchUser(StatesGroup):
    telegram_id = State()
    email_or_phone = State()


@admin_users.callback_query(F.data == "SearchByTgId", IsAdmin())
async def user_by_telegram_id(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text=f"{headerSearch}\n• Отправьте ID пользователя",
        reply_markup=await back_to("Отмена поиска", "BackToUsersMenu")
    )
    await state.set_state(SearchUser.telegram_id)


@admin_users.message(SearchUser.telegram_id, IsAdmin())
async def user_by_telegram_id(event: Message, state: FSMContext):
    await state.clear()
    user = await service.get_user_by_tg_id(int(event.text))
    if user:
        user = (
            f"👤 <b>{user.user_name}</b>\n"
            f"📧 {user.user_email}\n"
            f"📱 {user.user_phone}\n\n"
            # f"🧳 <b>Тур(ы):</b>\n{tours}"
        )
        await event.answer(f"{headUsersMain}\n• Пользователь:\n{user}", reply_markup=user_info().as_markup())
    else:
        await event.answer(f"{headUsersMain}\n• Пользователь c id:\n{event.text} не существует",
                           reply_markup=user_info().as_markup())


@admin_users.callback_query(F.data == "SearchByPhoneOrEmail", IsAdmin())
async def user_by_email_of_phone(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text=f"{headerSearch}\n• Отправьте почту или номер телефона пользователя",
        reply_markup=await back_to("Отмена поиска", "BackToUsersMenu")
    )
    await state.set_state(SearchUser.email_or_phone)


@admin_users.message(SearchUser.email_or_phone, IsAdmin())
async def user_by_email_of_phone(event: Message, state: FSMContext):
    await state.clear()
    user = await service.get_user_by_phone_or_email(event.text)
    if user:
        #tours = "\n".join([f"– {t.tour.tour_name}" for t in user.tours]) or "Нет туров"
        user = (
            f"👤 <b>{user['name']}</b>\n"
            f"📧 {user['email']}\n"
            f"📱 {user['phone']}\n\n"
            # f"🧳 <b>Тур(ы):</b>\n{tours}"
        )
        await event.answer(f"{headUsersMain}\n• Пользователь:\n\n{user}", reply_markup=user_info().as_markup())
    else:
        await event.answer(
            text=f"{headUsersMain}\n\n• Такого пользователя не существует",
            reply_markup=user_info().as_markup()
        )
