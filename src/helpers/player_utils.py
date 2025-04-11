from typing import TYPE_CHECKING

from bson import ObjectId

from data.items.utils import get_item
from helpers.cache import cached
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t


if TYPE_CHECKING:
    from database.models import UserItem, UserModel


@cached()
def calc_xp_for_level(level: int) -> float:
    return float(5 * level + 50 * level + 100)


def transfer_item(
    from_user: "UserModel",
    to_user: "UserModel",
    item_id: ObjectId,
    quantity: int = 1,
) -> str:
    try:
        user_item = from_user.inventory.get_by_id(id=item_id)
        assert user_item
        item = get_item(user_item.name)
    except NoResult:
        return t(from_user.lang, "item-not-found-in-inventory", item_name="?????")

    from_user.inventory.remove(user_item.name, quantity, id=user_item.id)

    if user_item.type == ItemType.USABLE:
        assert user_item.usage  # for linters
        to_user.inventory.add(user_item.name, quantity, user_item.usage)
        key = "transfer.success-usable"
    else:
        to_user.inventory.add(user_item.name, quantity)
        key = "transfer.success"

    return t(
        from_user.lang,
        key,
        from_user=from_user,
        to_user=to_user,
        usage=user_item.usage,
        quantity=quantity,
        item_name=item.name,
    )


def get_available_items_for_use(user: "UserModel") -> "list[UserItem]":
    def is_item_available(user_item: "UserItem"):
        item = get_item(user_item.name)
        if not item.is_consumable or user_item.quantity <= 0:
            return False
        if item.type == ItemType.USABLE and user_item.usage > 0:  # type: ignore
            return True
        if item.type == ItemType.STACKABLE:
            return True
        return False

    available_items = [
        user_item for user_item in user.inventory.items if is_item_available(user_item)
    ]
    return sorted(available_items, key=lambda item: item.quantity, reverse=True)
