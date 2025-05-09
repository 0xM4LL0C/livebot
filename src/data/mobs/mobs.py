import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from aiogram.types import CallbackQuery, Message

from data.items.items import ITEMS
from datatypes import Mob
from helpers.enums import ItemRarity
from helpers.localization import t
from helpers.markups import InlineMarkup


if TYPE_CHECKING:
    from database.models import UserModel


@dataclass
class Trader(Mob):
    async def on_meet(self, query: CallbackQuery, user: "UserModel"):
        assert isinstance(query.message, Message)  # for linters
        item = random.choice(
            list(
                filter(lambda i: (i.rarity == ItemRarity.COMMON) and (i.price is not None), ITEMS),
            )
        )

        quantity = random.randint(10, 20)
        assert item.price  # for linters
        price = quantity * item.price
        await query.message.edit_text(
            t(
                "mobs.trader.on-meet",
                mob=self,
                item=item,
                quantity=quantity,
                price=price,
            ),
            reply_markup=InlineMarkup.trader(
                user, item_name=item.name, price=price, quantity=quantity
            ),
        )


@dataclass
class Chest(Mob):
    async def on_meet(self, query: CallbackQuery, user: "UserModel"):
        assert isinstance(query.message, Message)  # for linters
        await query.message.edit_text(
            t(
                "mobs.chest.on-meet",
                mob=self,
            ),
            reply_markup=InlineMarkup.chest(user),
        )


MOBS: Final[list[Mob]] = [
    Trader(
        emoji="👳‍♂️",
        name="торговец",
        desc="Предлагает игроку купить предмет",
        chance=40.0,
    ),
    Chest(
        emoji="🧰",
        name="сундук",
        desc="Из него выпадают предметы",
        chance=12.7,
    ),
]
