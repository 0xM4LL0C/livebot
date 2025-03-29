from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.items.items import ITEMS
from data.items.utils import get_item_emoji
from database.models import UserModel
from helpers.callback_factory import CraftCallback, ShopCallback, TransferCallback
from helpers.enums import ItemType
from helpers.utils import pretty_float, pretty_int


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
                    item_name=item.translit(),
                    quantity=quantity,
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()

    @classmethod
    def craft_main(cls, quantity: int, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        available_items = list(filter(lambda item: item.craft, ITEMS))

        for item in available_items:
            assert item.craft  # for linters

            max_craftable = min(
                user.inventory.get(craft_item.name).quantity // craft_item.quantity
                for craft_item in item.craft
            )

            if max_craftable >= quantity > 0:
                builder.button(
                    text=f"{item.emoji} {item.name} ({pretty_int(max_craftable)})",
                    callback_data=CraftCallback(
                        item_name=item.translit(),
                        quantity=quantity,
                        user_id=user.id,
                    ),
                )

        builder.adjust(2)
        return builder.as_markup()

    @classmethod
    def transfer_usable_items(
        cls, user: UserModel, to_user: UserModel, item_name: str
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        items = user.inventory.get_all(item_name)
        items = list(filter(lambda i: i.type == ItemType.USABLE, items))  # type: ignore
        items.sort(key=lambda i: i.usage, reverse=True)  # type: ignore

        for item in items:
            assert item.usage
            builder.button(
                text=f"{get_item_emoji(item.name)} {pretty_float(item.usage)}%",
                callback_data=TransferCallback(
                    to_user_id=to_user.id,
                    item_oid=str(item.id),
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()
