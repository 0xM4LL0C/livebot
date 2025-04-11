import random
from contextlib import suppress
from datetime import timedelta

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from bson import ObjectId

from core.player_actions import game_action, sleep_action, walk_action, work_action
from data.achievements.utils import get_achievement
from data.items.items import ITEMS
from data.items.utils import get_item, get_item_count_for_rarity
from database.models import UserModel
from helpers.callback_factory import (
    AchievementsCallback,
    ChestCallback,
    CraftCallback,
    HomeCallback,
    QuestCallback,
    ShopCallback,
    TraderCallback,
    TransferCallback,
    UseCallback,
)
from helpers.enums import ItemRarity
from helpers.exceptions import ItemNotFoundError, NoResult
from helpers.localization import t
from helpers.markups import InlineMarkup
from helpers.player_utils import get_available_items_for_use, transfer_item
from helpers.stickers import Stickers
from helpers.utils import pretty_int

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
        try:
            user_item = user.inventory.get(craft.name)
            if user_item.quantity < craft.quantity * quantity:
                raise NoResult(craft.name)
        except NoResult:
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


@router.callback_query(UseCallback.filter())
async def use_callback(query: CallbackQuery, callback_data: UseCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    try:
        user_item = user.inventory.get_by_id(id=ObjectId(callback_data.item_oid))
    except NoResult:
        await query.answer(t(user.lang, "item-not-found-in-inventory", item_name="?????"))
        return

    if user_item.quantity <= 0:
        await query.answer(t(user.lang, "item-not-enough", item_name=user_item.name))
        return

    item = get_item(user_item.name)

    match item.name:
        case "трава" | "буханка" | "сэндвич" | "пицца" | "тако" | "суп":
            user.hunger += item.effect  # type: ignore
            mess = t(user.lang, "use.hunger", item_name=item.name, effect=item.effect)
        case "буст":
            xp = random.randint(100, 150)
            user.xp += xp
            mess = t(user.lang, "use.boost", item_name=item.name, xp=xp)
        case "бокс":
            num_items_to_get = random.randint(1, 3)
            items = ""

            for item_to_get in random.choices(ITEMS, k=num_items_to_get):
                quantity = get_item_count_for_rarity(item_to_get.rarity)

                items += f"+ {pretty_int(quantity)} {item_to_get.name} {item_to_get.emoji}\n"
                if item_to_get.name == "бабло":
                    user.coin += quantity
                else:
                    user.inventory.add(item_to_get.name, quantity)
            mess = t(user.lang, "use.box-opened", items=items)
        case "энергос" | "чай":
            user.fatigue += item.effect  # type: ignore
            mess = t(user.lang, "use.fatigue", item_name=item.name, effect=item.effect)
        case "пилюля":
            await query.message.reply(t(user.lang, "under-development"))
            return
        case "хелп":
            user.health += item.effect  # type: ignore
            mess = t(user.lang, "use.health", item_name=item.name, effect=item.effect)
        case "фиксоманчик":
            await query.message.reply(t(user.lang, "under-development"))
            return
        case "водка":
            user.fatigue = 100
            user.health -= item.effect  # type: ignore
            mess = t(user.lang, "use.vodka", item_name=item.name, effect=item.effect)
        case "велик":
            if not user.action or user.action.type != "walk":
                await query.message.reply("Ты не гуляешь")  # TODO: add translation
                return
            minutes = random.randint(10, 45)
            user.action.end -= timedelta(minutes=minutes)
            mess = t(user.lang, "use.bike", item_name=item.name, minutes=minutes)
        case "клевер-удачи":
            user.luck += item.effect  # type: ignore
            mess = t(user.lang, "use.luck", item_name=item.name, effect=item.effect)
        case "конфета":
            user.hunger += item.effect  # type: ignore
            user.fatigue += item.effect  # type: ignore
            mess = t(user.lang, "use.candy", item_name=item.name, effect=item.effect)
        case _:
            raise NotImplementedError(item.name)

    user.inventory.remove(user_item.name, 1, id=user_item.id)
    await user.check_status(chat_id=query.message.chat.id)
    await user.update_async()

    items = get_available_items_for_use(user)

    if items:  # pylint: disable=duplicate-code
        key = "use.available-items"
    else:
        key = "use.not-available-items"

    assert isinstance(query.message, Message)
    await query.message.edit_text(
        t(user.lang, key),
        reply_markup=InlineMarkup.use(items, user),
    )
    await query.message.reply(mess)


@router.callback_query(QuestCallback.filter())
async def quest_callback(query: CallbackQuery, callback_data: QuestCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    assert isinstance(query.message, Message)  # for linters
    if callback_data.action == "skip":
        if user.coin < user.new_quest_coin_quantity:
            await query.answer(t(user.lang, "item-not-enough", item_name="бабло"))
            return
        user.coin -= user.new_quest_coin_quantity
        user.new_quest_coin_quantity += random.randint(10, 20)
        user.new_quest()
        await query.message.delete()
        await user.update_async()
        await query.answer(t(user.lang, "quest.skipped"), show_alert=True)
        return

    if not user.quest.is_done:
        await query.answer(t(user.lang, "quest.quest-not-completed"))
        return

    for name, quantity in user.quest.needed_items.items():
        user.inventory.remove(name, quantity)

    user.coin += user.quest.reward
    user.xp += user.quest.xp
    old_quest = user.quest
    user.new_quest()
    user.achievements_info.incr_progress("квестоман")

    await user.update_async()
    await query.message.delete()
    await query.message.answer_sticker(Stickers.quest)
    await query.message.reply_to_message.reply(t(user.lang, "quest.complete", quest=old_quest))


@router.callback_query(HomeCallback.filter())
async def home_callback(query: CallbackQuery, callback_data: HomeCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    assert isinstance(query.message, Message)  # for liners

    match callback_data.action:
        case "actions":
            await query.message.edit_text(
                t(user.lang, "home.actions-choice"),
                reply_markup=InlineMarkup.home_actions_choice(user),
            )
        case "main-menu":
            await query.message.edit_text(
                t(user.lang, "home.main"),
                reply_markup=InlineMarkup.home_main(user),
            )
        case "walk":
            await walk_action(query, user)
        case "work":
            await work_action(query, user)
        case "sleep":
            await sleep_action(query, user)
        case "game":
            await game_action(query, user)


@router.callback_query(TraderCallback.filter())
async def trader_callback(query: CallbackQuery, callback_data: TraderCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    assert isinstance(query.message, Message)  # for liners

    if callback_data.action == "leave":
        await query.message.delete()
        await query.answer(t(user.lang, "mobs.trader.leave"), show_alert=True)
        return

    assert callback_data.item_name  # for linters
    assert callback_data.price  # for linters
    assert callback_data.quantity  # for linters

    item = get_item(callback_data.item_name)

    if user.coin < callback_data.price:
        await query.answer(
            t(user.lang, "item-not-enough", item_name="бабло"),
            show_alert=True,
        )
        return

    user.coin -= callback_data.price
    user.inventory.add(item.name, callback_data.quantity)
    await user.update_async()
    await query.message.delete()
    await query.message.answer(
        t(
            user.lang,
            "mobs.trader.trade",
            user=user,
            item=item,
            quantity=callback_data.quantity,
            price=callback_data.price,
        )
    )


@router.callback_query(ChestCallback.filter())
async def chest_callback(query: CallbackQuery, callback_data: ChestCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    assert isinstance(query.message, Message)  # for liners

    if callback_data.action == "leave":
        await query.message.delete()
        await query.answer(t(user.lang, "mobs.chest.leave"), show_alert=True)
        return

    try:
        key_item = user.inventory.get("ключ")
    except NoResult:
        await query.answer(
            t(user.lang, "item-not-found-in-inventory", item_name="ключ"), show_alert=True
        )
        return

    print(key_item.quantity, key_item.quantity < 1)

    items = ""
    items_quantity = random.randint(2, 3)
    available_items = list(
        filter(lambda i: i.rarity in (ItemRarity.COMMON, ItemRarity.UNCOMMON), ITEMS)
    )
    available_items = random.choices(available_items, k=items_quantity)

    for item in available_items:
        quantity = get_item_count_for_rarity(item.rarity)
        if item.name == "бабло":
            user.coin += quantity
        else:
            user.inventory.add(item.name, quantity)

        items += f"+ {pretty_int(quantity)} {item.name} {item.emoji}\n"

    user.inventory.remove(key_item.name, 1)
    user.achievements_info.incr_progress("кладоискатель")
    await user.update_async()

    await query.message.answer(t(user.lang, "mobs.chest.open", user=user, items=items))
    await query.message.delete()


@router.callback_query(AchievementsCallback.filter())
async def achievements_callback(query: CallbackQuery, callback_data: AchievementsCallback):
    if callback_data.user_id != query.from_user.id:
        return

    user = await UserModel.get_async(id=query.from_user.id)

    achievement = get_achievement(callback_data.achievement_name)
    user_achievement = user.achievements_info.get(achievement.name)

    await query.answer(
        t(
            user.lang,
            "achievements.info",
            achievement=achievement,
            user_achievement=user_achievement,
        ),
        show_alert=True,
    )
