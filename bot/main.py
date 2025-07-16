from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from tortoise import Tortoise

from bot.handlers.admin.admin_direction import admin_direct
from bot.handlers.admin.admin_lessons import admin_lessons
from bot.handlers.admin.admin_main import admin_main
from bot.handlers.admin.admin_tour import admin_tour
from bot.handlers.admin.admin_users import admin_users
from bot.handlers.user.payment_pre_checkout import payment
from bot.handlers.user.user_lesson import user_lesson
from bot.handlers.user.user_main import user_main
from bot.handlers.user.user_tour import user_tour
from bot.config import WEBAPP_HOST, WEBAPP_PORT
from bot.create import surf_bot, dp, init_db, container, app, web, WEBHOOK_URL, WEBHOOK_PATH


async def init_container(app):
    container.wire(
        packages=[
            "bot.handlers.admin",
            "bot.handlers.user"
        ]
    )

async def init_db_hook(app):
    await init_db()


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(bot: Bot):
    await Tortoise.close_connections()


def main():
    dp.include_routers(
        admin_main, admin_lessons, admin_tour, admin_direct, admin_users,
        user_main, user_lesson, user_tour, payment
    )

    app.on_startup.append(init_db_hook)
    app.on_startup.append(init_container)

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=surf_bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    setup_application(app, dp, bot=surf_bot)
    web.run_app(app, host=WEBAPP_HOST, port=int(WEBAPP_PORT))


if __name__ == "__main__":
    main()
