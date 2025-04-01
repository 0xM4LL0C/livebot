from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.items.items import ITEMS
from data.items.utils import get_item_emoji
from database.models import UserItem, UserModel
from datatypes import UserActionType
from helpers.callback_factory import (
    ChestCallback,
    CraftCallback,
    HomeCallback,
    QuestCallback,
    ShopCallback,
    TraderCallback,
    TransferCallback,
    UseCallback,
)
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.utils import pretty_float, pretty_int, quick_markup


class InlineMarkup:
    @classmethod
    def shop_main(cls, quantity: int, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        items = list(filter(lambda i: i.price, ITEMS))
        items.sort(key=lambda i: i.price)  # type: ignore

        for item in items:
            assert item.price  # for linters

            builder.button(
                text=f"{item.emoji} — {pretty_int(item.price * quantity)}",
                callback_data=ShopCallback(
                    item_name=item.translit(),
                    quantity=quantity,
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()

    @classmethod
    def craft_main(cls, quantity: int, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        available_items = list(filter(lambda item: item.craft, ITEMS))
        for item in available_items:
            assert item.craft  # for linters

            try:
                max_craftable = min(
                    user.inventory.get(craft_item.name).quantity // craft_item.quantity
                    for craft_item in item.craft
                )
            except NoResult:
                max_craftable = 0

            if max_craftable >= quantity > 0:
                builder.button(
                    text=f"{item.emoji} {item.name} ({pretty_int(max_craftable)})",
                    callback_data=CraftCallback(
                        item_name=item.translit(),
                        quantity=quantity,
                        user_id=user.id,
                    ),
                )

        builder.adjust(2)
        return builder.as_markup()

    @classmethod
    def transfer_usable_items(
        cls, user: UserModel, to_user: UserModel, item_name: str
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        items = user.inventory.get_all(item_name)
        items = list(filter(lambda i: i.type == ItemType.USABLE, items))  # type: ignore
        items.sort(key=lambda i: i.usage, reverse=True)  # type: ignore

        for item in items:
            assert item.usage
            builder.button(
                text=f"{get_item_emoji(item.name)} {pretty_float(item.usage)}%",
                callback_data=TransferCallback(
                    to_user_id=to_user.id,
                    item_oid=str(item.id),
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()

    @classmethod
    def use(cls, items: list[UserItem], user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for item in items:
            text = f"{get_item_emoji(item.name)} {pretty_int(item.quantity)}"
            if item.type == ItemType.USABLE:
                assert item.usage
                text += f" ({pretty_float(item.usage)}%)"
            builder.button(
                text=text,
                callback_data=UseCallback(
                    item_oid=str(item.id),
                    user_id=user.id,
                ),
            )

        builder.adjust(3)
        return builder.as_markup()

    @classmethod
    def quest(cls, user: UserModel) -> InlineKeyboardMarkup:
        if user.quest.is_done:
            finish_button_text = t(user.lang, "quest.buttons.done-text")
            text = t(user.lang, "quest.buttons.done", button_text=finish_button_text)
            callback_data = QuestCallback(action="done", user_id=user.id)
        else:
            finish_button_text = t(user.lang, "quest.buttons.skip")
            text = t(user.lang, "quest.buttons.done", button_text=finish_button_text)
            callback_data = QuestCallback(action="skip", user_id=user.id)

        return quick_markup({text: {"callback_data": callback_data}})

    @classmethod
    def home_main(cls, user: UserModel) -> InlineKeyboardMarkup:
        actions_button_text = t(user.lang, "home.buttons.open-actions")
        return quick_markup(
            {
                actions_button_text: {
                    "callback_data": HomeCallback(action="actions", user_id=user.id)
                }
            }
        )

    @classmethod
    def home_actions_choice(cls, user: UserModel) -> InlineKeyboardMarkup:
        def active_action_text(action: UserActionType, text: str) -> str:
            if user.is_current_action(action):
                return f"🔹 {text}"
            return text

        walk_text = active_action_text("walk", t(user.lang, "home.buttons.actions.walk"))
        work_text = active_action_text("work", t(user.lang, "home.buttons.actions.work"))
        sleep_text = active_action_text("sleep", t(user.lang, "home.buttons.actions.sleep"))
        game_text = active_action_text("game", t(user.lang, "home.buttons.actions.game"))
        return quick_markup(
            {
                walk_text: {"callback_data": HomeCallback(action="walk", user_id=user.id)},
                work_text: {"callback_data": HomeCallback(action="work", user_id=user.id)},
                sleep_text: {"callback_data": HomeCallback(action="sleep", user_id=user.id)},
                game_text: {"callback_data": HomeCallback(action="game", user_id=user.id)},
            },
            sizes=(2,),
        )

    @classmethod
    def trader(
        cls,
        user: UserModel,
        item_name: str,
        price: int,
        quantity: int,
    ) -> InlineKeyboardMarkup:
        trade_text = t(user.lang, "mobs.trader.buttons.trade")
        leave_text = t(user.lang, "mobs.buttons.leave")

        return quick_markup(
            {
                trade_text: {
                    "callback_data": TraderCallback(
                        action="trade",
                        item_name=item_name,
                        price=price,
                        quantity=quantity,
                        user_id=user.id,
                    )
                },
                leave_text: {"callback_data": TraderCallback(action="leave", user_id=user.id)},
            },
            sizes=(2,),
        )

    @classmethod
    def chest(cls, user: UserModel) -> InlineKeyboardMarkup:
        open_text = t(user.lang, "mobs.chest.buttons.open")
        leave_text = t(user.lang, "mobs.buttons.leave")

        return quick_markup(
            {
                open_text: {"callback_data": ChestCallback(action="open", user_id=user.id)},
                leave_text: {"callback_data": ChestCallback(action="leave", user_id=user.id)},
            },
            sizes=(2,),
        )

    @classmethod
    def update_action(cls, action: UserActionType, user: UserModel) -> InlineKeyboardMarkup:
        update_text = t(user.lang, "buttons.update")
        back_text = t(user.lang, "buttons.back")

        return quick_markup(
            {
                update_text: {"callback_data": HomeCallback(action=action, user_id=user.id)},
                back_text: {"callback_data": HomeCallback(action="actions", user_id=user.id)},
            }
        )
