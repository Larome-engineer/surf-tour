import asyncio

from bot.handlers.admin.admin_direction import admin_direct
from bot.handlers.admin.admin_lessons import admin_lessons
from bot.handlers.admin.admin_main import admin_main
from bot.handlers.admin.admin_tour import admin_tour
from bot.handlers.admin.admin_users import admin_users
from bot.handlers.user.payment_pre_checkout import payment
from bot.handlers.user.user_lesson import user_lesson
from bot.handlers.user.user_main import user_main
from bot.handlers.user.user_tour import user_tour
from create import surf_bot, dp, init_db, container


async def init_container():
    container.wire(
        packages=[
            "bot.handlers.admin",
            "bot.handlers.user"
        ]
    )


async def main():
    dp.include_routers(
        admin_main, admin_lessons, admin_tour, admin_direct, admin_users,
        user_main, user_lesson, user_tour, payment
    )

    await init_db()
    await init_container()
    await dp.start_polling(surf_bot)


if __name__ == "__main__":
    asyncio.run(main())
