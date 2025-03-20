from dataclasses import dataclass
from typing import Optional

import tomlkit


@dataclass
class GeneralConfig:
    owners: list[int]
    debug: bool = False


@dataclass
class DatabaseConfig:
    url: str
    name: str


@dataclass
class RedisConfig:
    url: str


@dataclass
class TelegramConfig:
    token: str
    log_chat_id: int
    log_thread_id: Optional[int] = None


@dataclass
class Config:
    general: GeneralConfig
    database: DatabaseConfig
    redis: RedisConfig
    telegram: TelegramConfig

    @staticmethod
    def from_file(path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = tomlkit.load(f)

        return Config(
            general=GeneralConfig(**data.get("general", {})),
            database=DatabaseConfig(**data.get("database", {})),
            redis=RedisConfig(**data.get("redis", {})),
            telegram=TelegramConfig(**data.get("telegram", {})),
        )
