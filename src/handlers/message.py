import asyncio
import random

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from consts import TELEGRAM_ID
from core.weather import get_weather
from data.items.utils import get_item, get_item_emoji
from database.models import PromoModel, UserModel
from helpers.datetime_utils import utcnow
from helpers.enums import ItemType
from helpers.exceptions import ItemNotFoundError, NoResult
from helpers.localization import t
from helpers.markups import InlineMarkup
from helpers.player_utils import (
    check_user_subscription,
    get_available_items_for_use,
    send_channel_subscribe_message,
    transfer_item,
)
from helpers.stickers import Stickers
from helpers.utils import (
    check_version,
    get_item_middle_price,
    pretty_float,
    pretty_int,
    sorted_dict,
)
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
            mess = t("new_referral_joined", name=user.name, coin=coin)

            await message.bot.send_message(from_user.id, mess)

    if user is None:
        user = await register_user(message)

    await message.reply(t("welcome", name=user.name))


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.reply(t("help"))


@router.message(Command("profile"))
async def profile_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t("profile", user=user))


@router.message(Command("inventory"))
async def inventory_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)
    items = ""

    for item in sorted(user.inventory.items, key=lambda i: i.quantity, reverse=True):
        if item.quantity <= 0:
            continue
        items += f"{get_item_emoji(item.name)} {item.name} {item.quantity}"
        if item.type == ItemType.USABLE:
            assert item.usage is not None  # for linters
            items += f" ({pretty_float(item.usage)} %)"  # pyright: ignore[reportAttributeAccessIssue]
        items += "\n"
    if not items:
        items = t("empty-inventory")
    await message.reply(t("inventory", items=items))


@router.message(Command("shop"))
async def shop_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if command.args:
        try:
            quantity = int(command.args)
        except ValueError:
            quantity = 1
    else:
        quantity = 1

    await message.reply(
        t("shop.main", quantity=quantity),
        reply_markup=InlineMarkup.shop_main(quantity, user),
    )


@router.message(Command("casino"))
async def casino_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    quantity = command.args

    if not quantity:
        await message.reply(t("casino.main"))
        return

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    try:
        ticket = user.inventory.get("билет")
    except NoResult:
        await message.reply(t("item-not-found-in-inventory", item_name="билет"))
        return

    if user.coin < quantity:
        await message.reply(t("item-not-enough", item_name="бабло"))
        return

    dice = await message.answer_dice("🎲")

    await asyncio.sleep(1)

    ticket.quantity -= 1

    if dice.dice.value > 3:
        user.coin += quantity * 2
        user.casino_info.win += quantity * 2
        await message.reply(t("casino.win", quantity=quantity * 2))
    else:
        user.coin -= quantity
        user.casino_info.loose += quantity
        await message.reply(t("casino.loose", quantity=quantity))

    await user.check_status(message.chat.id)
    await user.update_async()


@router.message(Command("craft"))
async def craft_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if command.args:
        try:
            quantity = int(command.args)
        except ValueError:
            quantity = 1
    else:
        quantity = 1

    await message.reply(t("craft.main"), reply_markup=InlineMarkup.craft_main(quantity, user))


@router.message(Command("transfer"))
async def transfer_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    args = str(command.args).strip().split()

    if len(args) < 2:
        await message.reply(t("transfer.help"))
        return

    item_name, quantity = args

    try:
        item = get_item(item_name)
    except ItemNotFoundError:
        await message.reply(t("item-not-exist", item_name=item_name))
        return

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    if not message.reply_to_message:
        await message.reply(t("reply-to-message-required"))
        return
    if (
        message.reply_to_message.from_user.is_bot
        or message.reply_to_message.from_user.id == TELEGRAM_ID
    ):
        return

    target_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)

    if item.name == "бабло":
        if user.coin < quantity:
            await message.reply(t("item-not-enough", item_name="бабло"))
            return
        user.coin -= quantity
        target_user.coin += quantity
        mess = t(
            "transfer.success",
            from_user=user,
            to_user=target_user,
            quantity=quantity,
            item_name=item.name,
        )
    elif item.type == ItemType.USABLE:
        await message.reply(
            t("select-which-one"),
            reply_markup=InlineMarkup.transfer_usable_items(
                user=user,
                to_user=target_user,
                item_name=item_name,
            ),
        )
        return
    else:
        user_item = user.inventory.get(item.name)
        mess = transfer_item(user, target_user, user_item.id, quantity=quantity)

    await user.update_async()
    await target_user.update_async()

    await message.reply(mess)


@router.message(Command("use"))
async def use_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    items = get_available_items_for_use(user)

    if items:
        key = "use.available-items"
    else:
        key = "use.not-available-items"

    await message.reply(
        t(key),
        reply_markup=InlineMarkup.use(items, user),
    )


@router.message(Command("ref"))
async def ref_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    link = f"https://t.me/{(await message.bot.me()).username}?start=ref_{user.id}"

    await message.reply(t("ref", link=link))


@router.message(Command("promo"))
async def promo_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    args = command.args

    if not args:
        await message.reply(t("promo.usage"))
        return

    try:
        promo = await PromoModel.get_async(code=args)
    except NoResult:
        await message.reply(t("promo.not-exists"))
        return

    if promo.is_used:
        await message.reply(t("promo.already-activated"))
        return

    await message.delete()
    if user.oid in promo.users:
        await message.reply(t("promo.user-already-activated"))
        return

    promo.users.add(user.oid)

    items = ""

    promo_items = sorted_dict(promo.items, reverse=True)

    for item_name, quantity in promo_items.items():
        item = get_item(item_name)

        if item.name == "бабло":  # pylint: disable=duplicate-code
            user.coin += quantity
        else:
            user.inventory.add(item.name, quantity)
        items += f"+ {pretty_int(quantity)} {item.name} {item.emoji}\n"

    await promo.update_async()
    await user.update_async()

    await message.answer_sticker(Stickers.promo)
    await message.answer(t("promo.activate", user=user, items=items))


@router.message(Command("quest"))
async def quest_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    assert user.quest  # for linters

    await message.reply(
        t("quest.main", quest=user.quest),
        reply_markup=InlineMarkup.quest(user),
    )


@router.message(Command("weather"))
async def weather_cmd(message: Message):
    weather = await get_weather()
    weather_type = t(f"weather.types.{weather.current.code.name.lower()}")
    await message.reply(t("weather.info", weather=weather, weather_type=weather_type))


@router.message(Command("price"))
async def price_cmd(message: Message, command: CommandObject):
    if not command.args:
        await message.reply(t("price.help"))
        return

    item_name = command.args.strip()

    try:
        item = get_item(item_name)
    except ItemNotFoundError:
        await message.reply(t("item-not-exist", item_name=item_name))
        return

    price = get_item_middle_price(item.name)
    await message.reply(t("price.price", item=item, price=price))


@router.message(Command("home"))
async def home_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t("home.main"), reply_markup=InlineMarkup.home_main(user))


@router.message(Command("rules"))
async def rules_cmd(message: Message):
    await UserModel.get_async(id=message.from_user.id)

    await message.reply(t("rules"), reply_markup=InlineMarkup.rules())


@router.message(Command("time"))
async def time_cmd(message: Message):
    await message.reply(t("time"))


@router.message(Command("violations"))
async def violations_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    violations = ""

    if not user.violations:
        violations = t("violation.none")
    else:
        for i, violation in enumerate(user.violations, start=1):
            until = t("violation.until", violation=violation) if violation else ""
            violations += f"{i} {violation.type} {until}"
            violations += f"    <i>{violation.reason}</i>"

    await message.reply(t("violation.info", violations=violations))


@router.message(Command("achievements"))
async def achievements_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    await message.reply(t("achievements.main"), reply_markup=InlineMarkup.achievements(user))


@router.message(Command("version"))
async def version_cmd(message: Message):
    await UserModel.get_async(id=message.from_user.id)

    await message.reply(
        t("version.info", status=await check_version()),
        reply_markup=InlineMarkup.version(),
    )


@router.message(Command("daily_gift"))
async def daily_gift_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    if not await check_user_subscription(user):
        await send_channel_subscribe_message(message)
        return

    if user.daily_gift.next_claim_available_at <= utcnow():
        user.new_daily_gift()
        await user.update_async()

    await message.reply(t("daily-gift.main"), reply_markup=InlineMarkup.daily_gift(user))
