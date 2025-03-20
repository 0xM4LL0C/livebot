from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.items.items import ITEMS
from database.models import UserModel
from helpers.callback_factory import ItemInfoCallback
from helpers.utils import batched


class InlineMarkup:
    @classmethod
    def items_help_main_menu(cls, user: UserModel, page: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        items = list(batched(ITEMS, 6))

        for item in items[page]:
            builder.button(
                text=f"{item.emoji} {item.name}",
                callback_data=ItemInfoCallback(
                    item_name=item.translit(),
                    current_page=page,
                    user_oid=str(user.oid),
                ),
            )

        return builder.as_markup()
