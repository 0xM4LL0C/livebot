from dataclasses import dataclass, field
from typing import Any, Optional

import tomlkit
from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass
class GeneralConfig:
    owners: list[int] = field(default_factory=list)
    debug: bool = False


@dataclass
class DatabaseConfig:
    url: str
    name: str = "livebot"


@dataclass
class RedisConfig:
    url: str


@dataclass
class TelegramConfig:
    token: str
    log_chat_id: int | str
    log_thread_id: Optional[int] = None


@dataclass
class Config(DataClassTOMLMixin):
    general: GeneralConfig
    database: DatabaseConfig
    redis: RedisConfig
    telegram: TelegramConfig

    def __post_serialize__(self, d: dict[Any, Any]) -> dict[Any, Any]:
        def remove_none_values(data: dict[Any, Any]) -> dict[Any, Any]:
            return {
                k: (remove_none_values(v) if isinstance(v, dict) else v)
                for k, v in data.items()
                if v is not None
            }

        return remove_none_values(d)

    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_toml(f.read(), decoder=tomlkit.loads)
