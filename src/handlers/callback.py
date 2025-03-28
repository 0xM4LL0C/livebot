from aiogram import Router
from aiogram.types import CallbackQuery, Message

from data.items.utils import get_item
from database.models import UserModel
from helpers.callback_factories import ShopCallback
from helpers.exceptions import ItemNotFoundError
from helpers.localization import t

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

    user_item = user.inventory.get_or_add(item.name)
    user_item.quantity += quantity
    user.coin -= price

    assert isinstance(query.message, Message)

    await query.message.reply_to_message.reply(
        t(user.lang, "shop.buy-item", quantity=quantity, item_name=item.name, price=price),
    )

    await user.update_async()
