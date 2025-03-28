from typing import ParamSpec, TypeVar

from data.items.items import ITEMS
from datatypes import Item
from helpers.exceptions import ItemNotFoundError
from helpers.utils import cached

P = ParamSpec("P")
T = TypeVar("T")


@cached
def get_item(name: str) -> Item:
    for item in ITEMS:
        if item.name == name:
            return item
        if item.altnames and item.name in item.altnames:
            return item
        if item.translit() == name:
            return item
    raise ItemNotFoundError(name)


@cached
def get_item_emoji(name: str) -> str:
    try:
        return get_item(name).emoji
    except ItemNotFoundError:
        return ""
