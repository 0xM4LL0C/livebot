import os
import sys

import tomlkit

config = tomlkit.document()
config["general"] = {
    "debug": False,
    "owners": [5161392463],
}
config["database"] = {
    "url": "your_db_url",
    "name": "livebot",
}
config["redis"] = {
    "url": "your_redis_url",
}
config["telegram"] = {
    "token": "your_bot_token",
    "log_chat_id": "",
    "log_thread_id": 2,
}
config["weather"] = {
    "region": "",
}
config["event"] = {
    "start_time": "",
    "end_time": "",
    "open": False,
}
config["channel"] = {
    "id": "",
    "chat_id": "",
}

if os.path.exists("config.toml"):
    print("Конфигурационный файл существует")
    sys.exit(1)

with open("config.toml", "w") as f:
    f.write(tomlkit.dumps(config))

print("Конфигурационный файл успешно создан.")
