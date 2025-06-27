import random
from contextlib import suppress
from datetime import timedelta

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from livebot.core.weather import get_weather
from livebot.data.items.utils import get_item, get_item_emoji
from livebot.data.mobs.utils import get_random_mob
from livebot.database.models import UserAction, UserModel
from livebot.helpers.datetime_utils import utcnow
from livebot.helpers.enums import WeatherCode
from livebot.helpers.localization import t
from livebot.helpers.markups import InlineMarkup
from livebot.helpers.utils import pretty_int


async def walk_action(query: CallbackQuery, user: UserModel):
    assert isinstance(query.message, Message)  # fol linters
    current_time = utcnow()
    if user.action is None:
        if user.hunger <= 20:
            await query.answer(t("too_hungry"), show_alert=True)
            return
        if user.fatigue <= 20:
            await query.answer(t("too_tired"), show_alert=True)
            return

        user.action = UserAction("walk", end=current_time + timedelta(hours=1))
        await user.update_async()
    elif not user.is_current_action("walk"):
        await query.answer(t("busy_with_something_else"), show_alert=True)
        return

    if current_time < user.action.end:
        time_left = user.action.end - current_time

        if time_left >= timedelta(minutes=random.randint(1, 5)):
            if mob := get_random_mob(user):
                await user.update_async()
                await mob.on_meet(query, user)
                return

        with suppress(TelegramBadRequest):  # for exception: message is not modified
            await query.message.edit_text(
                t("actions.walk.walking", time_left=time_left),
                reply_markup=InlineMarkup.update_action(user.action.type, user),
            )
        return

    weather = await get_weather()

    water = range(1, 2)

    if weather.current.code == WeatherCode.RAIN:
        water = range(5, 10)

    loot_table = [
        ("бабло", range(5, 20)),
        ("трава", range(1, 3)),
        ("гриб", range(1, 3)),
        ("вода", range(2, 5)),
        ("чаинка", range(1, 2)),
        ("вода", water),
    ]

    if weather.current.code == WeatherCode.SNOW:
        snow = range(5, 10)
        loot_table.append(("снег", snow))

    items = ""

    for item_name, item_range in loot_table:
        quantity = random.choice(item_range)

        items += f"+ {pretty_int(quantity)} {item_name} {get_item_emoji(item_name)}\n"
        if item_name == "бабло":
            user.coin += quantity
        else:
            user.inventory.add(item_name, quantity)

    user.xp += random.uniform(3.0, 5.0)
    user.action = None

    user.hunger -= random.randint(2, 5)
    user.fatigue -= random.randint(3, 8)
    user.mood -= random.randint(3, 6)
    user.met_mob = False
    user.notification_status.walk = False
    user.achievements_info.incr_progress("бродяга")

    await user.check_status(query.message.chat.id)
    await user.update_async()
    await query.message.edit_text(t("actions.walk.end", items=items))


async def work_action(query: CallbackQuery, user: UserModel):
    assert isinstance(query.message, Message)  # fol linters
    current_time = utcnow()
    if user.action is None:
        if user.hunger <= 20:
            await query.answer(t("too_hungry"), show_alert=True)
            return
        if user.fatigue <= 20:
            await query.answer(t("too_tired"), show_alert=True)
            return

        user.action = UserAction(
            "work",
            end=current_time
            + timedelta(hours=random.randint(2, 3), minutes=random.randint(10, 30)),
        )
        await user.update_async()
    elif not user.is_current_action("work"):
        await query.answer(t("busy_with_something_else"), show_alert=True)
        return

    if current_time < user.action.end:
        time_left = user.action.end - current_time

        with suppress(TelegramBadRequest):  # for exception: message is not modified
            await query.message.edit_text(
                t("actions.work.working", time_left=time_left),
                reply_markup=InlineMarkup.update_action(user.action.type, user),
            )
        return

    quantity = random.randint(100, 200) * user.level

    user.coin += quantity
    user.xp += random.uniform(5.0, 15.0)
    user.action = None
    user.hunger -= random.randint(5, 15)
    user.fatigue -= random.randint(10, 20)
    user.mood -= random.randint(3, 6)
    user.notification_status.work = False
    user.achievements_info.incr_progress("работяга")

    await user.check_status(query.message.chat.id)
    await user.update_async()
    await query.message.edit_text(t("actions.work.end", quantity=quantity))


async def sleep_action(query: CallbackQuery, user: UserModel):
    assert isinstance(query.message, Message)  # fol linters
    current_time = utcnow()
    if user.action is None:
        if user.hunger <= 20:
            await query.answer(t("too_hungry"), show_alert=True)
            return
        if user.fatigue <= 20:
            await query.answer(t("too_tired"), show_alert=True)
            return

        user.action = UserAction(
            "sleep",
            end=current_time + timedelta(hours=random.randint(6, 8)),
        )
        await user.update_async()
    elif not user.is_current_action("sleep"):
        await query.answer(t("busy_with_something_else"), show_alert=True)
        return

    if current_time < user.action.end:
        time_left = user.action.end - current_time

        with suppress(TelegramBadRequest):  # for exception: message is not modified
            await query.message.edit_text(
                t("actions.sleep.sleeping", time_left=time_left),
                reply_markup=InlineMarkup.update_action(user.action.type, user),
            )
        return

    fatigue = random.randint(50, 100)

    user.fatigue = fatigue
    user.xp += random.uniform(5.0, 15.0)
    user.action = None
    user.hunger -= random.randint(1, 3)
    user.mood += random.randint(1, 10)
    user.notification_status.sleep = False
    user.achievements_info.incr_progress("сонный")

    await user.check_status(query.message.chat.id)
    await user.update_async()
    await query.message.edit_text(t("actions.sleep.end", fatigue=fatigue))


async def game_action(query: CallbackQuery, user: UserModel):
    assert isinstance(query.message, Message)  # fol linters
    current_time = utcnow()
    if user.action is None:
        if user.hunger <= 20:
            await query.answer(t("too_hungry"), show_alert=True)
            return
        if user.fatigue <= 20:
            await query.answer(t("too_tired"), show_alert=True)
            return

        user.action = UserAction(
            "game",
            end=current_time
            + timedelta(hours=random.randint(0, 3), minutes=random.randint(15, 20)),
        )
        await user.update_async()
    elif not user.is_current_action("game"):
        await query.answer(t("busy_with_something_else"), show_alert=True)
        return

    if current_time < user.action.end:
        time_left = user.action.end - current_time

        with suppress(TelegramBadRequest):  # for exception: message is not modified
            await query.message.edit_text(
                t("actions.game.gaming", time_left=time_left),
                reply_markup=InlineMarkup.update_action(user.action.type, user),
            )
        return

    mood = random.randint(30, 60)

    user.mood = mood
    user.xp += random.uniform(3.0, 5.0)
    user.action = None
    user.hunger -= random.randint(2, 8)
    user.notification_status.game = False
    user.achievements_info.incr_progress("игроман")

    await user.check_status(query.message.chat.id)
    await user.update_async()
    await query.message.edit_text(t("actions.game.end", mood=mood))


async def fishing_action(query: CallbackQuery, user: UserModel):
    assert isinstance(query.message, Message)  # fol linters
    current_time = utcnow()
    if user.action is None:
        if user.hunger <= 20:
            await query.answer(t("too_hungry"), show_alert=True)
            return
        if user.fatigue <= 20:
            await query.answer(t("too_tired"), show_alert=True)
            return

        user.action = UserAction(
            "fishing",
            end=current_time + timedelta(hours=random.randint(1, 4)),
        )
        await user.update_async()
    elif not user.is_current_action("fishing"):
        await query.answer(t("busy_with_something_else"), show_alert=True)
        return

    if not user.inventory.has("удочка"):
        await query.answer(
            t("item-not-found-in-inventory", item_name="удочка"),
            show_alert=True,
        )
        return

    if current_time < user.action.end:
        time_left = user.action.end - current_time

        with suppress(TelegramBadRequest):  # for exception: message is not modified
            await query.message.edit_text(
                t("actions.fishing.fishing", time_left=time_left),
                reply_markup=InlineMarkup.update_action(user.action.type, user),
            )
        return

    item = get_item("рыба")
    quantity = random.randint(1, 4 * user.luck)

    rod = user.inventory.get("удочка")
    rod.use(random.uniform(*get_item(rod.name).strength_reduction))  # type: ignore

    user.inventory.add(item.name, quantity)

    user.action = None
    user.xp += random.uniform(4.7, 8.2)
    user.hunger -= random.randint(4, 8)
    user.fatigue -= random.randint(5, 10)
    user.mood -= random.randint(10, 15)
    user.notification_status.fishing = False
    user.achievements_info.incr_progress("рыбак")

    await user.check_status(query.message.chat.id)
    await user.update_async()
    await query.message.edit_text(t("actions.fishing.end", item=item, quantity=quantity))
