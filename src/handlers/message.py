import random

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from data.items.utils import get_item_emoji
from database.models import UserModel
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.utils import pretty_float
from middlewares.register import register_user

router = Router()


@router.message(CommandStart())
@router.message(CommandStart(deep_link=True))
async def start_cmd(message: Message, command: CommandObject):
    try:
        user = await UserModel.get_async(id=message.from_user.id)
    except NoResult:
        user = None

    if args := command.args:
        if args.startswith("ref_") and not user:
            from_user_id = int(args.replace("ref_", ""))
            from_user = await UserModel.get_async(id=from_user_id)

            coin = random.randint(5000, 15000)
            from_user.coin += coin
            from_user.achievements_info.incr_progress("друзья навеки")
            await from_user.update_async()

            user = await register_user(message)
            mess = t(from_user.lang, "new_referral_joined", name=user.name, coin=coin)

            await message.bot.send_message(from_user.id, mess)

    if user is None:
        user = await register_user(message)

    await message.reply(t(user.lang, "welcome", name=user.name))


@router.message(Command("help"))
async def help_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t(user.lang, "help"))


@router.message(Command("profile"))
async def profile_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t(user.lang, "profile", user=user))


@router.message(Command("bag"))
async def bag_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)
    items = ""

    for item in sorted(user.inventory.items, key=lambda i: i.quantity, reverse=True):
        items += f"{get_item_emoji(item.name)} {item.name} {item.quantity}"

        if item.type == ItemType.USABLE and item.usage:
            items += f" ({pretty_float(item.usage)} %)"  # pyright: ignore[reportAttributeAccessIssue]
        items += "\n"
    if not items:
        items = t(user.lang, "empty-inventory")
    await message.reply(t(user.lang, "inventory", items=items))


@router.message(Command("items"))
async def items_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)
    await message.reply(t(user.lang, "items-help"))


# ---------------------------------------------------------------------------- #


@router.message(F.content_type == ContentType.TEXT)
async def message_handler(message: Message):
    await message.reply(message.text)  # type: ignore
