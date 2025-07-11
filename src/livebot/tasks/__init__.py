import asyncio

from livebot.tasks.check import check
from livebot.tasks.notification import notification


async def setup_tasks():
    tasks = [
        check(),
        notification(),
    ]

    await asyncio.gather(*tasks)


def run_tasks():
    asyncio.create_task(setup_tasks())  # noqa
