from aiogram.filters.callback_data import CallbackData


class ItemInfoCallback(CallbackData, prefix="item_info"):
    item_name: str
    current_page: int
    user_id: str
