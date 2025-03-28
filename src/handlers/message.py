import asyncio
import random

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from data.items.utils import get_item_emoji
from database.models import UserModel
from helpers.enums import ItemType
from helpers.exceptions import ItemNotFoundError, NoResult
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
async def help_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t(user.lang, "help"))


@router.message(Command("profile"))
async def profile_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t(user.lang, "profile", user=user))


@router.message(Command("inventory"))
async def inventory_cmd(message: Message):
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


@router.message(Command("shop"))
async def shop_cmd(message: Message, command: CommandObject):
    raise NotImplementedError


@router.message(Command("casino"))
async def casino_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    quantity = command.args

    if not quantity:
        await message.reply(t(user.lang, "casino.main"))
        return

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    try:
        ticket = user.inventory.get_item("билет")
    except ItemNotFoundError:
        await message.reply(t(user.lang, "item-not-found-in-inventory", item_name="билет"))
        return

    if user.coin < quantity:
        await message.reply(t(user.lang, "item-not-enough", item_name="бабло"))
        return

    dice = await message.answer_dice("🎲")

    await asyncio.sleep(1)

    ticket.quantity -= 1

    if dice.dice.value > 3:
        user.coin += quantity * 2
        user.casino_info.win += quantity * 2
        await message.reply(t(user.lang, "casino.win", quantity=quantity * 2))
    else:
        user.coin -= quantity
        user.casino_info.loose += quantity
        await message.reply(t(user.lang, "casino.loose", quantity=quantity))

    await user.check_status(message.chat.id)
    await user.update_async()


# ---------------------------------------------------------------------------- #


@router.message(F.content_type == ContentType.TEXT)
async def message_handler(message: Message):
    await message.reply(message.text)  # type: ignore
