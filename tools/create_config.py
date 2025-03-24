import os
import sys

import tomlkit

config = {
    "general": {
        "debug": False,
        "owners": [5161392463],
    },
    "database": {
        "url": "your_db_url",
        "name": "livebot",
    },
    "redis": {
        "url": "your_redis_url",
    },
    "telegram": {
        "token": "your_bot_token",
        "log_chat_id": "",
        "log_thread_id": 2,
    },
    "weather": {
        "region": "",
    },
    "event": {
        "start_time": "",
        "end_time": "",
        "open": False,
    },
    "channel": {
        "id": "",
        "chat_id": "",
    },
}


if os.path.exists("config.toml"):
    print("Конфигурационный файл существует")
    sys.exit(1)

with open("config.toml", "w") as f:
    tomlkit.dump(config, f)

print("Конфигурационный файл успешно создан.")
