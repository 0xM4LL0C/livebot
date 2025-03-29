from aiogram.filters.callback_data import CallbackData


class ShopCallback(CallbackData, prefix="shop"):
    item_name: str
    quantity: int
    user_id: int


class CraftCallback(CallbackData, prefix="craft"):
    item_name: str
    quantity: int
    user_id: int
