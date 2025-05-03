from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import After, Scene, on
from aiogram.types import CallbackQuery, Message

from database.models import MarketItemModel, UserModel
from helpers.callback_factory import MarketCallback
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.markups import InlineMarkup
from helpers.utils import get_item_middle_price


class AddMarketItemFinalScene(
    Scene,
    state="add_market_item__final",
):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext):
        user = await UserModel.get_async(id=message.from_user.id)

        data = await state.get_data()
        item_oid = data["item_oid"]
        quantity = data["quantity"]
        price = data["price"]

        try:
            user_item = user.inventory.get_by_id(item_oid)
        except NoResult:
            await message.reply(t("item-not-found-in-inventory", item_name="???"))
            return
        if user_item.quantity < quantity:
            await message.reply(t("item-not-enough", item_name=user_item.name))
            return

        market_item = MarketItemModel(
            name=user_item.name,
            price=price,
            quantity=quantity,
            owner_oid=user.oid,
            usage=user_item.usage,
        )

        user.inventory.remove(name=user_item.name, id=user_item.id)
        await market_item.add_async()
        await user.update_async()

        await message.answer(t("market.user-sold-item", user=user, item=market_item))


class AddMarketItemSelectPriceScene(
    Scene,
    state="add_market_item__select_price",
):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext):
        user = await UserModel.get_async(id=message.from_user.id)
        item_oid = await state.get_value("item_oid")

        assert item_oid is not None  # for lintes

        user_item = user.inventory.get_by_id(item_oid)
        price = get_item_middle_price(user_item.name)

        if price:
            key = "input-price__with_middle_price"
        else:
            key = "input-price"

        await message.reply(t(key, price=price))

    @on.message(after=After.goto(AddMarketItemFinalScene))
    async def select_price(self, message: Message, state: FSMContext):
        try:
            if not message.text:
                raise ValueError
            price = int(message.text)
        except ValueError:
            await message.reply("invalid-input__int_excepted")
            return

        if price == 0:
            price = 1

        await state.update_data(price=price)


class AddMarketItemSelectQuantityScene(
    Scene,
    state="add_market_item__select_quantity",
):
    @on.callback_query.enter()
    async def on_enter_callback(self, query: CallbackQuery, state: FSMContext):
        await query.answer()

        assert isinstance(query.message, Message)  # for linters

        await self.on_enter(query.message.reply_to_message, state=state)

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext):
        user = await UserModel.get_async(id=message.from_user.id)
        item_oid = await state.get_value("item_oid")

        assert item_oid is not None  # for lintes

        user_item = user.inventory.get_by_id(item_oid)

        if user_item.type == ItemType.USABLE:
            await state.update_data(quantity=1)
            await self.wizard.goto(AddMarketItemSelectPriceScene)
            return

        await message.reply(t("input-quantity"))

    @on.message(after=After.goto(AddMarketItemSelectPriceScene))
    async def input_quantity(self, message: Message, state: FSMContext):
        try:
            if not message.text:
                raise ValueError

            quantity = int(message.text)
        except ValueError:
            quantity = 1

        user = await UserModel.get_async(id=message.from_user.id)
        item_oid = await state.get_value("item_oid")

        assert item_oid  # for linters

        user_item = user.inventory.get_by_id(id=item_oid)

        if user_item.quantity < quantity:
            await message.reply(t("item-not-enough", item_name=user_item.name))
            await self.wizard.exit()
            return

        await state.update_data(quantity=quantity)


class AddMarketItemMainScene(
    Scene,
    state="add_market_item",
    reset_data_on_enter=True,
    reset_history_on_enter=True,
):
    @on.callback_query.enter()
    async def on_enter(
        self,
        query: CallbackQuery,
    ):
        user = await UserModel.get_async(id=query.from_user.id)

        if not user.inventory.items:
            await query.answer(t("market.no-items"), show_alert=True)
            await self.wizard.exit()

        assert isinstance(query.message, Message)  # for linters

        await query.message.edit_text(
            t("select-which-one"),
            reply_markup=InlineMarkup.market_add_item__select_item(user),
        )

    @on.callback_query(
        MarketCallback.filter(F.action == "select-item"),
        after=After.goto(AddMarketItemSelectQuantityScene),
    )
    async def select_item(
        self,
        query: CallbackQuery,
        callback_data: MarketCallback,
        state: FSMContext,
    ):
        user = await UserModel.get_async(id=query.from_user.id)
        assert callback_data.item_oid  # for linters

        try:
            item = user.inventory.get_by_id(callback_data.item_oid)
        except NoResult:
            await query.answer(t("item-not-found-in-inventory", item_name="???"), show_alert=True)
            await self.wizard.exit()
            return

        await state.update_data(item_oid=item.id)
