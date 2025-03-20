from aiogram.exceptions import TelegramAPIError

from config import bot
from database.models import UserModel
from helpers.datetime_utils import utcnow
from helpers.utils import antiflood, quick_markup


async def _notification():
    users = await UserModel.get_all_async()

    for user in users:
        await user.fetch_async()

        if not user.action:
            continue
        try:
            current_time = utcnow()
            if user.action.end <= current_time:
                if user.action.type == "street" and not user.notification_status.walk:
                    user.notification_status.walk = True
                    mess = "Ты закончил прогулку"
                elif user.action.type == "work" and not user.notification_status.work:
                    user.notification_status.work = True
                    mess = "Ты закончил работу"
                elif user.action.type == "sleep" and not user.notification_status.sleep:
                    user.notification_status.sleep = True
                    mess = "Ты проснулся"
                elif user.action.type == "game" and not user.notification_status.game:
                    user.notification_status.game = True
                    mess = "Ты проснулся"
                else:
                    continue

                markup = quick_markup({"Дом": {"callback_data": f"open home {user.id}"}})
                await antiflood(bot.send_message(user.id, mess, reply_markup=markup))

        except TelegramAPIError:
            continue

        await user.update_async()


async def notification():
    while True:
        await _notification()
