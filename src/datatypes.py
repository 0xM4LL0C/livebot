from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

import transliterate

from helpers.cache import cached
from helpers.enums import ItemRarity, ItemType, WeatherType

if TYPE_CHECKING:
    from database.models import UserModel

ChatIdType = int | str


# ---------------------------------- weather --------------------------------- #

weather_types = {
    "1": WeatherType.THUNDERSTORM,
    "3": WeatherType.DRIZZLE,
    "5": WeatherType.RAIN,
    "6": WeatherType.SNOW,
    "7": WeatherType.FOG,
    "800": WeatherType.CLEAR,
    "80": WeatherType.CLOUDS,
}

weather_emojis = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Drizzle": "🌦️",
    "Rain": "🌧️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Smoke": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌫️",
    "Fog": "🌫️",
    "Sand": "🌫️",
    "Ash": "🌫️",
    "Squall": "🌫️",
    "Tornado": "🌪️",
}

wmo_weather_codes = {
    0: "Clear",
    1: "Clouds",
    2: "Clouds",
    3: "Clouds",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Drizzle",
    57: "Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Rain",
    67: "Rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow",
    80: "Rain",
    81: "Rain",
    82: "Rain",
    85: "Snow",
    86: "Snow",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}

wmo_weather_codes_ru = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Мелкий дождь",
    53: "Умеренный дождь",
    55: "Сильный дождь",
    56: "Морозный дождь",
    57: "Сильный морозный дождь",
    61: "Слабый дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Слабый снегопад",
    73: "Умеренный снегопад",
    75: "Сильный снегопад",
    77: "Снежные зерна",
    80: "Ливень",
    81: "Умеренный ливень",
    82: "Сильный ливень",
    85: "Слабый снег",
    86: "Сильный снег",
    95: "Гроза",
    96: "Гроза с градом",
    99: "Сильная гроза с градом",
}


class BaseWeather:
    def __init__(self, weather_code: int):
        self.weather_code: int = weather_code

    @property
    def type(self) -> str:
        return wmo_weather_codes.get(self.weather_code, "Unknown")

    @property
    def emoji(self) -> str:
        return weather_emojis.get(self.type, "❓")

    @property
    def ru_type(self) -> str:
        return wmo_weather_codes_ru.get(self.weather_code, "Неизвестно")


class HourlyWeather(BaseWeather):
    def __init__(self, data: dict[str, Any]) -> None:
        self.time: list[datetime] = list(
            map(lambda t: datetime.fromisoformat(t), data.get("time", []))
        )
        self.temperature_2m: list[float | int] = data.get("temperature_2m", [])


class HourlyUnits:
    def __init__(self, data: dict[str, Any]) -> None:
        self.temperature_2m: str = data.get("temperature_2m", "°C")
        self.time: str = data.get("time", "iso8601")
        self.weather_code: str = data.get("weather_code", "wmo code")


class CurrentWeather(BaseWeather):
    def __init__(self, data: dict[str, Any]) -> None:
        self.time: datetime = datetime.fromisoformat(data.get("time", ""))
        self.interval: int = data.get("interval", 0)
        self.temperature_2m: float = data.get("temperature_2m", 0.0)
        self.weather_code: int = data.get("weather_code", 0)


class CurrentUnits:
    def __init__(self, data: dict[str, Any]):
        self.time: str = data.get("time", "iso8601")
        self.interval: int = data.get("interval", "seconds")
        self.temperature_2m: float = data.get("temperature_2m", "°C")
        self.weather_code: int = data.get("weather_code", "wmo code")


class WeatherData:
    def __init__(self, data: dict[str, Any]):
        self.data: dict[str, Any] = data
        self.latitude: float = data.get("latitude", 0.0)
        self.longitude: float = data.get("latitude", 0.0)
        self.elevation: float = data.get("elevation", 0.0)
        self.generationtime_ms: float = data.get("generationtime_ms", 0.0)  # cspell: disable-line
        self.utc_offset_seconds: int = data.get("utc_offset_seconds", 0)
        self.timezone: str = data.get("timezone", "GMT")
        self.timezone_abbreviation: str = data.get("timezone_abbreviation", "GMT")
        self.hourly_units: HourlyUnits = HourlyUnits(data.get("hourly_units", {}))
        self.hourly: HourlyWeather = HourlyWeather(data.get("hourly", {}))
        self.current_units: CurrentUnits = CurrentUnits(data.get("current_units", {}))
        self.current: CurrentWeather = CurrentWeather(data.get("current", {}))


# ----------------------------------- item ----------------------------------- #
@dataclass
class ItemCraft:
    name: str
    quantity: int


@dataclass
class Item:
    name: str
    emoji: str
    desc: str
    rarity: ItemRarity
    type: ItemType = ItemType.STACKABLE
    is_task_item: bool = False
    can_exchange: bool = False
    is_consumable: bool = False
    altnames: Optional[list[str]] = None
    craft: Optional[list[ItemCraft]] = None
    effect: Optional[int] = None
    price: Optional[int] = None
    task_coin: Optional[range] = None
    exchange_price: Optional[range] = None
    strength: Optional[float] = None
    strength_reduction: Optional[tuple[float, float]] = None
    can_equip: bool = False

    @cached
    def translit(self) -> str:
        return transliterate.translit(self.name, reversed=True)


# ------------------------------- achievement ------------------------------- #


@dataclass
class AchievementReward:
    name: str
    quantity: int


@dataclass
class Achievement:
    name: str
    emoji: str
    desc: str
    need: int
    reward: list[AchievementReward]
    key: str = field(init=False)

    def __post_init__(self):
        self.key = self.name.strip().replace(" ", "-")

    def __str__(self) -> str:
        return f"{self.name}"

    def check(self, user: "UserModel") -> bool:
        progress = user.achievement_progress.get(self.key, 0)
        return progress >= self.need

    @cached
    def translit(self) -> str:
        return transliterate.translit(self.key, reversed=True)
