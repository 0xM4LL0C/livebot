import asyncio
import os
from typing import Any

import aiohttp


async def get_github_release_info(version: str) -> dict[Any, Any]:
    url = f"https://api.github.com/repos/0xM4LL0C/livebot/releases/tags/{version}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            release_info = await response.json()  # type: dict
            return release_info


async def send_release_notification():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    release_version = os.getenv("GITHUB_REF")

    if not bot_token or not chat_id or not release_version:
        raise ValueError

    release_version = release_version.split("/")[-1]

    release = await get_github_release_info(release_version)  # type: dict
    body: str = release["body"]

    for line in body.splitlines():
        if line.startswith("###"):
            new_line = f"*{line}*"
            body = body.replace(line, new_line)

    message = (
        f"*{'Пре-р' if release.get('prerelease') else 'Р'}елиз — {release.get('name')}* ✨\n\n"
        f"{body}"
    )

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "markdown",
        "disable_web_page_preview": True,
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                print(await response.text())
            response.raise_for_status()


if __name__ == "__main__":
    asyncio.run(send_release_notification())
