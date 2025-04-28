from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery, Message

from database.models import UserModel
from helpers.callback_factory import MarketCallback
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.markups import InlineMarkup


class AddMarketItemScene(
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

    @on.callback_query(MarketCallback.filter(F.action == "select-item"))
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
