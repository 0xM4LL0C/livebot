from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import logger
from consts import COIN_EMOJI, MARKET_ITEMS_LIST_MAX_ITEMS_COUNT, REPO_URL, VERSION
from data.achievements.utils import get_achievement
from data.items.items import ITEMS
from data.items.utils import get_item_emoji
from database.models import MarketItemModel, UserItem, UserModel
from datatypes import UserActionType
from helpers.callback_factory import (
    AchievementsCallback,
    ChestCallback,
    CraftCallback,
    DailyGiftCallback,
    HomeCallback,
    MarketCallback,
    QuestCallback,
    ShopCallback,
    TraderCallback,
    TransferCallback,
    UseCallback,
)
from helpers.enums import ItemType
from helpers.exceptions import NoResult
from helpers.localization import t
from helpers.utils import batched, pretty_float, pretty_int, quick_markup


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
            finish_button_text = t("quest.buttons.done-text")
            text = t("quest.buttons.done", button_text=finish_button_text)
            callback_data = QuestCallback(action="done", user_id=user.id)
        else:
            finish_button_text = t("quest.buttons.skip")
            text = t("quest.buttons.done", button_text=finish_button_text)
            callback_data = QuestCallback(action="skip", user_id=user.id)

        return quick_markup({text: {"callback_data": callback_data}})

    @classmethod
    def home_main(cls, user: UserModel) -> InlineKeyboardMarkup:
        actions_button_text = t("home.buttons.open-actions")
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

        walk_text = active_action_text("walk", t("home.buttons.actions.walk"))
        work_text = active_action_text("work", t("home.buttons.actions.work"))
        sleep_text = active_action_text("sleep", t("home.buttons.actions.sleep"))
        game_text = active_action_text("game", t("home.buttons.actions.game"))
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
        trade_text = t("mobs.trader.buttons.trade")
        leave_text = t("mobs.buttons.leave")

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
        open_text = t("mobs.chest.buttons.open")
        leave_text = t("mobs.buttons.leave")

        return quick_markup(
            {
                open_text: {"callback_data": ChestCallback(action="open", user_id=user.id)},
                leave_text: {"callback_data": ChestCallback(action="leave", user_id=user.id)},
            },
            sizes=(2,),
        )

    @classmethod
    def update_action(cls, action: UserActionType, user: UserModel) -> InlineKeyboardMarkup:
        update_text = t("buttons.update")
        back_text = t("buttons.back")

        return quick_markup(
            {
                update_text: {"callback_data": HomeCallback(action=action, user_id=user.id)},
                back_text: {"callback_data": HomeCallback(action="actions", user_id=user.id)},
            }
        )

    @classmethod
    def rules(cls) -> InlineKeyboardMarkup:
        read_text = t("read")
        return quick_markup({read_text: {"url": "https://0xM4LL0C.github.io/livebot/rules"}})

    @classmethod
    def achievements(cls, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for user_achievement in user.achievements_info.achievements:
            achievement = get_achievement(user_achievement.name)
            builder.button(
                text=f"{achievement.emoji} {achievement.name}",
                callback_data=AchievementsCallback(
                    achievement_name=achievement.translit(),
                    user_id=user.id,
                ),
            )

        builder.adjust(2)
        return builder.as_markup()

    @classmethod
    def version(cls) -> InlineKeyboardMarkup:
        return quick_markup(
            {t("version.buttons.release"): {"url": REPO_URL + f"releases/tag/v{VERSION}"}}
        )

    @classmethod
    def daily_gift(cls, user: UserModel) -> InlineKeyboardMarkup:
        def get_text():
            if user.daily_gift.is_claimed:
                return t("daily-gift.buttons.not-available", user=user)
            return t("daily-gift.buttons.available")

        return quick_markup({get_text(): {"callback_data": DailyGiftCallback(user_id=user.id)}})

    @classmethod
    def market_main(
        cls,
        page: int,
        user: UserModel,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        items = MarketItemModel.get_all()
        items.sort(key=lambda i: i.published_at, reverse=True)
        try:
            items = batched(items, MARKET_ITEMS_LIST_MAX_ITEMS_COUNT)[page]
        except IndexError:
            items = []

        for item in items:
            builder.button(
                text=(
                    f"{pretty_int(item.quantity)} {get_item_emoji(item.name)} - {pretty_int(item.price)} {COIN_EMOJI}"
                    + ("(" + pretty_float(item.usage) + ")" if item.usage else "")
                ),
                callback_data=MarketCallback(
                    action="view",
                    item_oid=str(item.oid),
                    current_page=page,
                    user_id=user.id,
                ),
            )

        builder.adjust(1)
        builder.row(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=MarketCallback(
                    action="back", current_page=page, user_id=user.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🛍",
                callback_data=MarketCallback(
                    action="kiosk", current_page=page, user_id=user.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=MarketCallback(
                    action="next", current_page=page, user_id=user.id
                ).pack(),
            ),
        )
        return builder.as_markup()

    @classmethod
    def market_item_view(
        cls, current_page: int, market_item: MarketItemModel, user: UserModel
    ) -> InlineKeyboardMarkup:
        return quick_markup(
            {
                t("market.buy", item=market_item): {
                    "callback_data": MarketCallback(
                        action="buy",
                        current_page=current_page,
                        item_oid=str(market_item.oid),
                        user_id=user.id,
                    )
                },
                t("buttons.back"): {
                    "callback_data": MarketCallback(
                        action="goto",
                        current_page=current_page,
                        user_id=user.id,
                    )
                },
            }
        )

    @classmethod
    def market_kiosk(cls, current_page: int, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="👀",
                callback_data=MarketCallback(
                    action="my-items",
                    current_page=current_page,
                    user_id=user.id,
                ).pack(),
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=MarketCallback(
                    action="add",
                    current_page=current_page,
                    user_id=user.id,
                ).pack(),
            ),
        )

        builder.row(
            InlineKeyboardButton(
                text=t("buttons.back"),
                callback_data=MarketCallback(
                    action="goto",
                    current_page=current_page,
                    user_id=user.id,
                ).pack(),
            )
        )

        return builder.as_markup()

    @classmethod
    def market_add_item__select_item(cls, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for item in sorted(user.inventory.items, key=lambda i: i.quantity, reverse=True):
            usage = f" ({pretty_float(item.usage)}%)" if item.usage else ""
            builder.button(
                text=f"{get_item_emoji(item.name)}{usage} {pretty_int(item.quantity)}",
                callback_data=MarketCallback(
                    action="select-item",
                    item_oid=str(item.id),
                    user_id=user.id,
                ),
            )
        builder.adjust(3)
        return builder.as_markup()

    @classmethod
    def market_my_items(cls, user: UserModel) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        market_items = MarketItemModel.get_all(
            owner_oid=str(user.oid)
        )  # Не знаю почему, но работает только если `user.oid` с типом str

        logger.debug(str(len(market_items)))

        for item in market_items:
            logger.debug(item.name + "\t" + str(item))
            builder.button(
                text=f"{pretty_int(item.quantity)} {get_item_emoji(item.name)} - {pretty_int(item.price)} {COIN_EMOJI}"
                + ("(" + pretty_float(item.usage) + ")" if item.usage else ""),
                callback_data=MarketCallback(
                    action="delete",
                    item_oid=str(item.oid),
                    user_id=user.id,
                ),
            )

        builder.adjust(1)
        return builder.as_markup()
