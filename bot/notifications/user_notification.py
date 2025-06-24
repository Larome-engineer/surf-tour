from bot.create import surf_bot
from utils.plural_form import get_plural_form


async def notify_about_places(users_list, name, places: int):
    send = 0
    not_send = 0
    for u in users_list:
        try:
            await surf_bot.send_message(
                chat_id=u,
                text=f"На тур {name} "
                     f"появилось {get_plural_form(places, 'место', 'места', 'мест')}"
            )
            send += 1
        except Exception as ex:
            not_send += 1
            continue
    return await send, not_send
