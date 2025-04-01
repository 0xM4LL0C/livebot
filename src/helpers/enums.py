from enum import Enum, auto


class Locations(Enum):
    HOME = "дом"


class ItemRarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


class ItemType(Enum):
    USABLE = auto()
    STACKABLE = auto()


class WeatherCode(Enum):
    CLEAR = range(0, 1)
    CLOUDS = range(1, 4)
    FOG = range(45, 49)
    DRIZZLE = range(51, 58)
    RAIN = list(range(61, 68)) + list(range(80, 83))
    SNOW = list(range(71, 78)) + list(range(85, 87))
    THUNDERSTORM = range(95, 96)
    THUNDERSTORM_WITH_HAIL = range(96, 100)

    @classmethod
    def get(cls, code: int) -> "WeatherCode":
        for weather_code in cls:
            if code in weather_code.value:
                return weather_code
        raise ValueError(code)
