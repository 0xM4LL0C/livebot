from typing import Literal

from aiogram.filters.callback_data import CallbackData


class ShopCallback(CallbackData, prefix="shop"):
    action: Literal["buy"]
    item_name: str
    quantity: int
    user_id: int
