import asyncio
import random
from itertools import filterfalse

from database.models import UserModel
from helpers.datetime_utils import utcnow


async def _check():
    users = await UserModel.get_all_async()

    for user in users:
        print(user.oid)
        await user.fetch_async()
        match random.randint(0, 5):
            case 0:
                user.hunger += 1
            case 1:
                user.fatigue += 1
            case 2:
                user.mood -= 1

        user.violations = list(
            filterfalse(
                lambda v: v.until_date and v.until_date < utcnow(),
                user.violations,
            )
        )

        await user.check_status()
        await user.update_async()


async def check():
    while True:
        await _check()
        await asyncio.sleep(3600)  # 1h
