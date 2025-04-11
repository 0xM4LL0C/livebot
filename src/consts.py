from typing import Final

from bson import ObjectId
from semver import Version
from xdg_base_dirs import xdg_cache_home, xdg_config_home, xdg_data_home


APP_NAME = "livebot"

CONFIG_DIR = xdg_config_home() / APP_NAME
CACHE_DIR = xdg_cache_home() / APP_NAME
DATA_DIR = xdg_data_home() / APP_NAME

COIN_EMOJI: Final = "🪙"
TELEGRAM_ID: Final = 777000
EMPTY_OBJECTID: Final = ObjectId("000000000000000000000000")

MINUTE: Final = 60
HOUR: Final = MINUTE * 60
DAY: Final = HOUR * 24
WEEK: Final = DAY * 7

with (DATA_DIR / "version").open("r", encoding="utf-8") as f:
    VERSION = Version.parse(f.read())
