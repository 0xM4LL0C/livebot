from typing import Literal, Optional

from aiogram.filters.callback_data import CallbackData


class ShopCallback(CallbackData, prefix="shop"):
    item_name: str
    quantity: int
    user_id: int


class CraftCallback(CallbackData, prefix="craft"):
    item_name: str
    quantity: int
    user_id: int


class TransferCallback(CallbackData, prefix="transfer"):
    to_user_id: int
    item_oid: str
    user_id: int


class UseCallback(CallbackData, prefix="use"):
    item_oid: str
    user_id: int


class QuestCallback(CallbackData, prefix="quest"):
    action: Literal["done", "skip"]
    user_id: int


class HomeCallback(CallbackData, prefix="home"):
    action: Literal["actions", "main-menu", "walk", "work", "sleep", "game"]
    user_id: int


class TraderCallback(CallbackData, prefix="trader"):
    action: Literal["trade", "leave"]
    item_name: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None
    user_id: int


class ChestCallback(CallbackData, prefix="chest"):
    action: Literal["open", "leave"]
    user_id: int
