from dataclasses import dataclass, field, fields
from datetime import UTC, datetime
from typing import Any

import aiohttp
from mashumaro import DataClassDictMixin, field_options

from livebot.config import config
from livebot.consts import HOUR
from livebot.helpers.cache import cached
from livebot.helpers.enums import WeatherCode


WEATHER_EMOJIS = {
    WeatherCode.CLEAR: "☀️",
    WeatherCode.CLOUDS: "☁️",
    WeatherCode.FOG: "🌫️",
    WeatherCode.DRIZZLE: "🌦️",
    WeatherCode.RAIN: "🌧️",
    WeatherCode.SNOW: "❄️",
    WeatherCode.THUNDERSTORM: "⛈️",
}


@dataclass
class WeatherInfo(DataClassDictMixin):
    time: datetime = field(
        metadata=field_options(deserialize=lambda d: datetime.fromisoformat(d).astimezone(UTC))
    )
    temperature: float = field(metadata=field_options(alias="temperature_2m"))
    code: WeatherCode = field(
        metadata=field_options(alias="weather_code", deserialize=lambda c: WeatherCode.get(c))
    )

    @property
    def emoji(self) -> str:
        return WEATHER_EMOJIS[self.code]


@dataclass
class Weather(DataClassDictMixin):
    latitude: float
    longitude: float
    current: WeatherInfo
    hourly: list[WeatherInfo] = field(default_factory=list)

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        keys = set(field.name for field in fields(cls))
        d = {key: value for key, value in d.items() if key in keys}

        if "hourly" in d and isinstance(d["hourly"], dict):
            hourly_data = d["hourly"]
            d["hourly"] = [
                {"time": time, "temperature_2m": temp, "weather_code": code}
                for time, temp, code in zip(
                    hourly_data["time"], hourly_data["temperature_2m"], hourly_data["weather_code"]
                )
            ]

        return d


@cached(expire=HOUR)
async def _get_coords_for_region(name: str) -> tuple[float, float]:
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": name,
        "count": 1,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data: dict[str, list[dict[str, Any]]] = await response.json()

    return data["results"][0]["latitude"], data["results"][0]["longitude"]


@cached(expire=HOUR)
async def get_weather() -> Weather:
    coords = await _get_coords_for_region(config.general.weather_region)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "current": ["temperature_2m", "weather_code"],
        "hourly": ["temperature_2m", "weather_code"],
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
    return Weather.from_dict(data)
