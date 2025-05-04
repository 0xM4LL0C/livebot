import asyncio
from contextlib import suppress

from aiogram.exceptions import TelegramAPIError

from config import bot
from database.models import UserModel
from helpers.cache import ram_cache
from helpers.datetime_utils import utcnow
from helpers.localization import t
from helpers.utils import antiflood


async def _notification():
    users = await UserModel.get_all_async()

    for user in users:
        if cached_value := ram_cache.get(f"lock-{user.id}"):
            ev, _ = cached_value
            ev: asyncio.Event
            if ev.is_set():
                continue

        await user.fetch_async()

        messages: set[str] = set()

        if user.action and user.action.is_done:
            if user.action.type == "walk" and not user.notification_status.walk:
                user.notification_status.walk = True
                messages.add(t(f"notifications.end-{user.action.type}"))
            elif user.action.type == "work" and not user.notification_status.work:
                user.notification_status.work = True
                messages.add(t(f"notifications.end-{user.action.type}"))
            elif user.action.type == "sleep" and not user.notification_status.sleep:
                user.notification_status.sleep = True
                messages.add(t(f"notifications.end-{user.action.type}"))
            elif user.action.type == "game" and not user.notification_status.game:
                user.notification_status.game = True
                messages.add(t(f"notifications.end-{user.action.type}"))
        if user.health < 30:
            ...
        if user.fatigue < 30:
            ...
        if user.hunger < 30:
            ...
        if user.mood < 30:
            ...
        if (
            user.daily_gift.next_claim_available_at <= utcnow()
            and not user.notification_status.daily_gift
        ):
            user.notification_status.daily_gift = True
            messages.add(t("notifications.daily-gift-available"))

        with suppress(TelegramAPIError):
            for message in messages:
                await antiflood(bot.send_message(user.id, message))

        await user.update_async()


async def notification():
    event = asyncio.Event()
    while True:
        if event.is_set():
            continue

        try:
            event.set()
            await _notification()
        finally:
            event.clear()
        await asyncio.sleep(15)
