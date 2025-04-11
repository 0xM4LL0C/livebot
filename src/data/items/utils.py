import random
from typing import ParamSpec, TypeVar

from data.items.items import ITEMS
from datatypes import Item
from helpers.enums import ItemRarity
from helpers.exceptions import ItemNotFoundError
from helpers.utils import cached


P = ParamSpec("P")
T = TypeVar("T")


@cached()
def get_item(name: str) -> Item:
    for item in ITEMS:
        if item.name == name:
            return item
        if item.altnames and item.name in item.altnames:
            return item
        if item.translit() == name:
            return item
    raise ItemNotFoundError(name)


@cached()
def get_item_emoji(name: str) -> str:
    return get_item(name).emoji


@cached()
def get_item_count_for_rarity(rarity: ItemRarity) -> int:
    match rarity:
        case ItemRarity.COMMON:
            quantity = random.randint(10, 20)
        case ItemRarity.UNCOMMON:
            quantity = random.randint(6, 8)
        case ItemRarity.RARE:
            quantity = random.randint(3, 5)
        case ItemRarity.EPIC:
            quantity = random.randint(1, 2)
        case ItemRarity.LEGENDARY:
            quantity = 1
        case _:
            raise NotImplementedError(f"Unknown rarity: {rarity}")
    return quantity
