from dataclasses import dataclass, field
from typing import Optional

import tomlkit
from mashumaro.config import BaseConfig as MashumaroBaseConfig
from mashumaro.mixins.toml import DataClassTOMLMixin


class _BaseConfig(DataClassTOMLMixin):
    class Config(MashumaroBaseConfig):
        omit_none = True


@dataclass
class GeneralConfig(_BaseConfig):
    owners: list[int] = field(default_factory=list)
    debug: bool = False


@dataclass
class DatabaseConfig(_BaseConfig):
    url: str
    name: str = "livebot"


@dataclass
class RedisConfig(_BaseConfig):
    url: str


@dataclass
class TelegramConfig(_BaseConfig):
    token: str
    log_chat_id: int | str
    log_thread_id: Optional[int] = None


@dataclass
class Config(_BaseConfig):
    general: GeneralConfig
    database: DatabaseConfig
    redis: RedisConfig
    telegram: TelegramConfig

    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_toml(f.read(), decoder=tomlkit.loads)
