from typing import TYPE_CHECKING

from aiogram.enums import ChatMemberStatus
from aiogram.types import Message
from bson import ObjectId

from config import bot, config
from data.items.utils import get_item
from helpers.cache import cached
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.utils import quick_markup


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
        return t("item-not-found-in-inventory", item_name="?????")

    from_user.inventory.remove(user_item.name, quantity, id=user_item.id)

    if user_item.type == ItemType.USABLE:
        assert user_item.usage  # for linters
        to_user.inventory.add(user_item.name, quantity, user_item.usage)
        key = "transfer.success-usable"
    else:
        to_user.inventory.add(user_item.name, quantity)
        key = "transfer.success"

    return t(
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


async def check_user_subscription(user: "UserModel") -> bool:
    tg_user = await bot.get_chat_member(config.telegram.channel_id, user.id)
    if tg_user.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    ]:
        return True
    return False


async def send_channel_subscribe_message(message: Message):
    chat_info = await message.bot.get_chat(config.telegram.channel_id)
    markup = quick_markup({"Подписаться": {"url": f"t.me/{chat_info.username}"}})
    mess = "Чтобы использовать эту функцию нужно подписаться на новостной канал"
    await message.reply(mess, reply_markup=markup)
