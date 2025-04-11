import asyncio
import random
from datetime import timedelta
from itertools import filterfalse

from database.models import UserModel
from helpers.cache import ram_cache
from helpers.datetime_utils import utcnow


async def _check():
    users = await UserModel.get_all_async()

    for user in users:
        if cached_value := ram_cache.get(f"lock-{user.id}"):
            ev, _ = cached_value
            ev: asyncio.Event
            while ev.is_set():
                await asyncio.sleep(0.5)

        if user.last_checked_at >= utcnow() - timedelta(minutes=1):
            continue
        await user.fetch_async()
        user.last_checked_at = utcnow()

        match random.randint(0, 5):
            case 0:
                user.hunger -= 1
            case 1:
                user.fatigue -= 1
            case 2:
                user.mood -= 1

        user.violations = list(
            filterfalse(
                lambda v: v.until_date and v.until_date < utcnow(),
                user.violations,
            ),
        )

        await user.check_status()
        await user.update_async()


async def check():
    while True:
        await _check()
        await asyncio.sleep(60)  # 1 min
