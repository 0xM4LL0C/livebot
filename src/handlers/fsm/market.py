from aiogram import Router
from aiogram.fsm.state import State, StatesGroup


router = Router()


class AddMarketItemState(StatesGroup):
    item_oid = State()
    quantity = State()
    price = State()
