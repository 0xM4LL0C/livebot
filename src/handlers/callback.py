import random
from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from bson import ObjectId

from data.items.utils import get_item
from database.models import UserModel
from helpers.callback_factory import CraftCallback, ShopCallback, TransferCallback
from helpers.exceptions import ItemNotFoundError
from helpers.localization import t
from helpers.markups import InlineMarkup
from helpers.player_utils import transfer_item

router = Router()


@router.callback_query(ShopCallback.filter())
async def shop_callback(query: CallbackQuery, callback_data: ShopCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    try:
        item = get_item(callback_data.item_name)
    except ItemNotFoundError as e:
        await query.answer(t(user.lang, "item-not-exist", item_name=str(e)), show_alert=True)
        return

    assert item.price  # for linters
    quantity = callback_data.quantity
    price = item.price * quantity

    if user.coin < price:
        await query.answer(text=t(user.lang, "item-not-enough", item_name="бабло"), show_alert=True)
        return

    user.inventory.add(item.name, quantity)

    user.coin -= price

    assert isinstance(query.message, Message)

    await query.message.reply_to_message.reply(
        t(user.lang, "shop.buy-item", quantity=quantity, item_name=item.name, price=price),
    )

    await user.update_async()


@router.callback_query(CraftCallback.filter())
async def craft_callback(query: CallbackQuery, callback_data: CraftCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    assert callback_data.item_name

    try:
        item = get_item(callback_data.item_name)
    except ItemNotFoundError as e:
        await query.answer(t(user.lang, "item-not-exist", item_name=str(e)), show_alert=True)
        return

    assert item.craft  # for linters

    quantity = callback_data.quantity

    for craft in item.craft:
        user_item = user.inventory.add_and_get(craft.name)
        if user_item.quantity <= 0 or user_item.quantity < craft.quantity * quantity:
            await query.answer(t(user.lang, "item-not-enough", item_name=craft.name))
            return
        user.inventory.remove(user_item.name, craft.quantity * quantity)

    user.inventory.add(item.name, quantity)

    xp = random.uniform(5.0, 10.0)

    if random.randint(1, 100) < user.luck:
        xp += random.uniform(2.3, 6.7)

    user.xp += xp
    await user.check_status()
    await user.update_async()

    assert isinstance(query.message, Message)

    with suppress(TelegramBadRequest):
        await query.message.edit_reply_markup(reply_markup=InlineMarkup.craft_main(quantity, user))

    await query.message.reply_to_message.reply(
        t(
            user.lang,
            "craft.craft-item",
            quantity=quantity,
            item_name=item.name,
            xp=xp,
        )
    )


@router.callback_query(TransferCallback.filter())
async def transfer_callback(query: CallbackQuery, callback_data: TransferCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)
    target_user = await UserModel.get_async(id=callback_data.to_user_id)

    mess = transfer_item(user, target_user, ObjectId(callback_data.item_oid))

    await query.message.answer(mess)
