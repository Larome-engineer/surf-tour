from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_edit, safe_answer, safe_edit_text
from bot.keyboards.admin import *
from database import service

admin_users = Router()

CHANGE = "<b>ПОИСК ПОЛЬЗОВАТЕЛЯ</b>"
LIST = "<b>📋 СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ 📋</b>"
SEARCH = "<b>🔎 ПОИСК ПОЛЬЗОВАТЕЛЯ 🔎</b>"
MENU = "<b>👨🏻‍💻 ПОЛЬЗОВАТЕЛИ\n| ГЛАВНОЕ МЕНЮ</b>"


####### USERS #######
@admin_users.callback_query(F.data == "Users", IsAdmin())
async def users(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, f"{MENU}", reply_markup=user_menu())


@admin_users.callback_query(F.data == "UsersList", IsAdmin())
async def get_all_users(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    user_list = await service.get_all_users()
    if not user_list:
        await safe_edit_text(
            event, f"{MENU}\n\n• В базе пока нет пользователей",
            reply_markup=user_menu()
        )
        return

    result = [f"{LIST}\n"]
    # for i, user in enumerate(user_list, start=1):
    #     result.append(
    #         f"<b>#{i}. {user['name'] if user['name'] is not None else "Нет имени"}</b>\n"
    #         f"🔜<code>{user['tg_id']}</code>\n"
    #         f"📝 {user['phone'] if user['phone'] is not None else "Нет номера"}\n"
    #         f"👥 {user['email'] if user['email'] is not None else "Нет почты"}\n"
    #     )

    await safe_edit_text(
        event,
        text=f"{'\n'.join(result)}",
        reply_markup=build_users_pagination_keyboard(
            users=user_list,
            page=0,
            back_callback="Users"
        )
    )


@admin_users.callback_query(lambda c: (
        c.data.startswith("UsersList_page:") or
        c.data.startswith("InfoAboutUser_")
), IsAdmin())
async def user_get_info(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_answer(event)
    if event.data.startswith("LessonsList_page:"):
        users_list = await service.get_all_users()
        page = int(event.data.split(":")[1])
        await safe_edit_text(
            event,
            f"{LIST}\n<b>• Страница {page + 1}</b>",
            reply_markup=build_users_pagination_keyboard(
                users=users_list,
                page=page,
                back_callback="Users"
            )
        )
    else:
        user = await service.get_user_by_tg_id(int(event.data.split("_")[1]))
        if not user:
            await safe_edit_text(
                event,
                f"{MENU}\n\n• Пользователь c id:\n{event.text} не существует",
                reply_markup=build_users_pagination_keyboard(
                    users=await service.get_all_users(),
                    page=0,
                    back_callback="Users"
                )
            )
            return
        user = (
            f"👤 <b>{user['name']}</b>\n"
            f"📧 {user['email']}\n"
            f"📱 {user['phone']}\n\n"
            # f"🧳 <b>Тур(ы):</b>\n{tours}"
            # f"🧳 <b>Урок(и):</b>\n{lessons}"
        )
        await safe_edit_text(
            event,
            f"{MENU}\n\n• Пользователь:\n{user}",
            reply_markup=build_users_pagination_keyboard(
                users=await service.get_all_users(),
                page=0,
                back_callback="Users"
            )
        )


@admin_users.callback_query(F.data == "UsersInfo", IsAdmin())
async def user_get_info(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(event, state, f"{SEARCH}\n• Выбери опцию поиска", reply_markup=user_info())


class SearchUser(StatesGroup):
    telegram_id = State()
    email_or_phone = State()


@admin_users.callback_query(F.data.startswith("SearchByTgId"), IsAdmin())
async def user_by_telegram_id(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event, state,
        text=f"{SEARCH}\n• Отправьте ID пользователя",
        reply_markup=back_to("Отмена поиска", "BackToUsersMenu")
    )
    await state.set_state(SearchUser.telegram_id)


@admin_users.message(SearchUser.telegram_id, IsAdmin())
async def user_by_telegram_id(event: Message, state: FSMContext):
    await state.clear()
    await safe_answer(event)

    user = await service.get_user_by_tg_id(int(event.text))
    if not user:
        await event.answer(
            f"{MENU}\n• Пользователь c id:\n{event.text} не существует",
            reply_markup=user_info()
        )
        return
    user = (
        f"👤 <b>{user.user_name}</b>\n"
        f"📧 {user.user_email}\n"
        f"📱 {user.user_phone}\n\n"
        # f"🧳 <b>Тур(ы):</b>\n{tours}"
    )
    await event.answer(f"{MENU}\n• Пользователь:\n{user}", reply_markup=user_info())


@admin_users.callback_query(F.data == "SearchByPhoneOrEmail", IsAdmin())
async def user_by_email_of_phone(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event, state,
        text=f"{SEARCH}\n• Отправьте почту или номер телефона пользователя",
        reply_markup=back_to("Отмена поиска", "BackToUsersMenu")
    )
    await state.set_state(SearchUser.email_or_phone)


@admin_users.message(SearchUser.email_or_phone, IsAdmin())
async def user_by_email_of_phone(event: Message, state: FSMContext):
    await state.clear()
    user = await service.get_user_by_phone_or_email(event.text)
    if not user:
        await event.answer(text=f"{MENU}\n\n• Такого пользователя не существует", reply_markup=user_info())
        return
        # tours = "\n".join([f"– {t.tour.tour_name}" for t in user.tours]) or "Нет туров"
    user = (
        f"👤 <b>{user['name']}</b>\n"
        f"📧 {user['email']}\n"
        f"📱 {user['phone']}\n\n"
        # f"🧳 <b>Тур(ы):</b>\n{tours}"
    )
    await event.answer(f"{MENU}\n• Пользователь:\n\n{user}", reply_markup=user_info())
