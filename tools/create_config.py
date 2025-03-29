import os
import sys

import tomlkit
import tomlkit.items

sys.path.insert(0, "src")

from config_types import Config, DatabaseConfig, GeneralConfig, RedisConfig, TelegramConfig

with open("version") as f:
    version = f.read().strip()

config = tomlkit.document()
config.add(
    tomlkit.items.Comment(
        tomlkit.items.Trivia(
            comment=f"#:schema https://raw.githubusercontent.com/0xM4LL0C/livebot/refs/tags/v{version}/config_schema.json"
        )
    )
)
config.add(tomlkit.nl())
config.add(tomlkit.comment("config docs: https://0xM4LL0C.github.io/livebot/dev/config/"))


default_config = Config(
    general=GeneralConfig(),
    database=DatabaseConfig(url="database_url"),
    redis=RedisConfig(url="redis_url"),
    telegram=TelegramConfig(token="bot token from @BotFather", log_chat_id="log chat id"),
)

config.update(default_config.to_dict())

if os.path.exists("config.toml"):
    print("Конфигурационный файл существует")
    sys.exit(1)

with open("config.toml", "w") as f:
    f.write(tomlkit.dumps(config))

print("Конфигурационный файл успешно создан.")
