import asyncio
import logging

from handlers.admin import admin
from handlers.user import user
from create import surf_bot, dp, init_db

async def main():
    dp.include_routers(admin, user)
    await init_db()
    await dp.start_polling(surf_bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=f'[BOT] '
               f'{u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"}')
    asyncio.run(main())