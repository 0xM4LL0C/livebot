from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.items.items import ITEMS
from database.models import UserModel
from helpers.callback_factories import ShopCallback
from helpers.utils import pretty_int


class InlineMarkup:
    @classmethod
    def shop_main(cls, quantity: int, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        items = list(filter(lambda i: i.price, ITEMS))
        items.sort(key=lambda i: i.price)  # type: ignore

        for item in items:
            assert item.price  # for linters

            builder.button(
                text=f"{item.emoji} — {pretty_int(item.price * quantity)}",
                callback_data=ShopCallback(
                    action="buy",
                    item_name=item.translit(),
                    quantity=quantity,
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()
