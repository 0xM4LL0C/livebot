from typing import Final

from aiogram.types import InlineKeyboardButton
from bson import ObjectId

PAGER_CONTROLLERS: Final = [
    InlineKeyboardButton(text="↩️", callback_data="{name} start {pos} {user_id}"),
    InlineKeyboardButton(text="⬅️", callback_data="{name} back {pos} {user_id}"),
    InlineKeyboardButton(text="➡️", callback_data="{name} next {pos} {user_id}"),
    InlineKeyboardButton(text="↪️", callback_data="{name} end {pos} {user_id}"),
]

COIN_EMOJI: Final = "🪙"
TELEGRAM_ID: Final = 777000
EMPTY_OBJECTID: Final = ObjectId("000000000000000000000000")

MINUTE: Final = 60
HOUR: Final = MINUTE * 60
DAY: Final = HOUR * 24
WEEK: Final = DAY * 7
