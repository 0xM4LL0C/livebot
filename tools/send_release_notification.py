import os
from typing import Any

import httpx


def get_github_release_info(version: str) -> dict[Any, Any]:
    url = f"https://api.github.com/repos/0xM4LL0C/livebot/releases/tags/{version}"
    response = httpx.get(url)

    response.raise_for_status()
    release_info = response.json()  # type: dict
    return release_info


def send_release_notification():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    release_version = os.getenv("GITHUB_REF")

    if not bot_token or not chat_id or not release_version:
        raise ValueError

    release_version = release_version.split("/")[-1]

    release = get_github_release_info(release_version)  # type: dict
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

    response = httpx.post(url, json=payload)
    if not response.is_success:
        print(response.text)
    response.raise_for_status()


if __name__ == "__main__":
    send_release_notification()
