from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import transliterate

from helpers.cache import cached, cached_method
from helpers.enums import ItemRarity, ItemType

if TYPE_CHECKING:
    from database.models import UserModel


ChatIdType = int | str


@dataclass
class ItemCraft:
    name: str
    quantity: int


@dataclass
class Item:
    name: str
    emoji: str
    desc: str
    rarity: ItemRarity
    type: ItemType = ItemType.STACKABLE
    is_quest_item: bool = False
    can_exchange: bool = False
    is_consumable: bool = False
    altnames: Optional[list[str]] = None
    craft: Optional[list[ItemCraft]] = None
    effect: Optional[int] = None
    price: Optional[int] = None
    quest_coin: Optional[range] = None
    exchange_price: Optional[range] = None
    strength: Optional[float] = None
    strength_reduction: Optional[tuple[float, float]] = None
    can_equip: bool = False

    @cached_method
    def translit(self) -> str:
        return transliterate.translit(self.name, reversed=True)


# ------------------------------- achievement ------------------------------- #


@dataclass
class AchievementReward:
    name: str
    quantity: int


@dataclass
class Achievement:
    name: str
    emoji: str
    desc: str
    need: int
    reward: list[AchievementReward]
    key: str = field(init=False)

    def __post_init__(self):
        self.key = self.name.strip().replace(" ", "-")

    def __str__(self) -> str:
        return f"{self.name}"

    def check(self, user: "UserModel") -> bool:
        progress = user.achievements_info.progress.get(self.key, 0)
        return progress >= self.need

    @cached
    def translit(self) -> str:
        return transliterate.translit(self.key, reversed=True)
