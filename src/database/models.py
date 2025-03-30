import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal, Optional
from weakref import ReferenceType, ref

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bson import ObjectId
from mashumaro import field_options

from config import bot
from data.achievements.utils import get_achievement
from data.items.items import ITEMS
from data.items.utils import get_item, get_item_emoji
from database.base import BaseModel, SubModel
from datatypes import Achievement, ChatIdType
from helpers.datetime_utils import utcnow
from helpers.enums import ItemType, Locations
from helpers.exceptions import AchievementNotFoundError, NoResult
from helpers.player_utils import calc_xp_for_level
from helpers.stickers import Stickers
from helpers.utils import calc_percentage, create_progress_bar


@dataclass
class CasinoInfo(SubModel):
    win: int = 0
    loose: int = 0

    @property
    def profit(self) -> int:
        return self.win - self.loose


@dataclass
class UserAction(SubModel):
    type: Literal["street", "work", "sleep", "game"]
    end: datetime
    start: datetime = field(default_factory=utcnow)


@dataclass
class UserNotificationStatus(SubModel):
    walk: bool = False
    work: bool = False
    sleep: bool = False
    game: bool = False
    health: bool = False
    mood: bool = False
    hunger: bool = False
    fatigue: bool = False


@dataclass
class UserItem(SubModel):
    name: str
    quantity: int = 0
    usage: Optional[float] = None
    id: ObjectId = field(default_factory=ObjectId)

    def __post_init__(self):
        if self.type == ItemType.USABLE and not self.usage:
            self.usage = 0.0

    @property
    def type(self) -> ItemType:
        return get_item(self.name).type

    def add(self, amount: int):
        if self.type == ItemType.STACKABLE:
            self.quantity += amount
        else:
            raise ValueError("Cannot add quantity to a usable item")

    def remove(self, amount: int):
        if self.type == ItemType.STACKABLE:
            if amount > self.quantity:
                raise ValueError("Not enough items to remove")
            self.quantity -= amount
        else:
            raise ValueError("Cannot remove quantity from a usable item")

    def use(self, amount: float):
        if self.type == ItemType.USABLE:
            if self.usage is None or amount > self.usage:
                raise ValueError("Not enough usage percentage left")
            self.usage -= amount
        else:
            raise ValueError("Cannot use a stackable item")


@dataclass
class Inventory(SubModel):
    items: list[UserItem] = field(default_factory=list)

    def add(self, name: str, count: int = 1, usage: float = 100.0):
        item = get_item(name)

        if item.type == ItemType.USABLE:
            for _ in range(count):
                self.items.append(UserItem(name=name, quantity=1, usage=usage))
        elif item.type == ItemType.STACKABLE:
            for inv_item in self.items:
                if inv_item.name == name:
                    inv_item.quantity += count
                    return
            self.items.append(UserItem(name=name, quantity=count))

    def remove(
        self,
        name: str,
        count: int = 1,
        id: Optional[ObjectId] = None,
    ) -> Optional[UserItem]:
        for item in self.items:
            if item.name == name and (id is None or item.id == id):
                if item.type == ItemType.USABLE:
                    return self.items.pop(self.items.index(item))
                if item.type == ItemType.STACKABLE:
                    item.quantity -= count
                    if item.quantity <= 0:
                        self.items.remove(item)
                        return
                    return item

    def add_and_get(self, name: str) -> UserItem:
        self.add(name)
        return self.get(name)

    def get_all(self, name: str) -> list[UserItem]:
        return [item for item in self.items if item.name == name and item.quantity > 0]

    def get_by_id(self, id: ObjectId) -> UserItem:
        try:
            return [item for item in self.items if item.id == id and item.quantity > 0][0]
        except IndexError as e:
            raise NoResult(id) from e

    def get(self, name: str) -> UserItem:
        items = self.get_all(name)
        if items:
            return items[0]
        self.add(name)
        return self.get_all(name)[0]

    def has(self, name: str) -> bool:
        return self.get_all(name) != []

    def use(self, name: str, amount: float):
        for item in self.items:
            if item.name == name and item.type == ItemType.USABLE:
                assert item.usage  # for linters
                item.usage = max(0.0, item.usage - amount)
                if item.usage == 0.0:
                    self.items.remove(item)
                return


@dataclass
class UserAchievement(SubModel):
    name: str
    completed_at: datetime = field(default_factory=utcnow)


@dataclass
class AchievementsInfo(SubModel):
    achievements: list[UserAchievement] = field(default_factory=list)
    progress: dict[str, int] = field(default_factory=dict)
    _user: ReferenceType["UserModel"] = field(
        init=False, repr=False, metadata=field_options(serialize="omit")
    )

    def get_progress_bar(self, name: str) -> str:
        ach = get_achievement(name)
        progress = self.progress.get(ach.name, 0)
        percentage = min(100.0, calc_percentage(progress, ach.need))
        progress_bar = f"Выполнено: {progress}/{ach.need}"
        progress_bar += f"[{create_progress_bar(percentage)}] {percentage:.2f}%"
        return progress_bar

    def is_completed(self, name: str) -> bool:
        try:
            self.get(name)
            return True
        except AchievementNotFoundError:
            return False

    async def award(self, achievement: Achievement):
        if not self._user():
            return
        if self.is_completed(achievement.name):
            return

        user_achievement = UserAchievement(achievement.name)
        self.achievements.append(user_achievement)

        reward = ""

        for item in achievement.reward:
            reward += f" + {item.quantity} {item.name} {get_item_emoji(item.name)}"

            if item.name == "бабло":
                self._user().coin += item.quantity
            else:
                self._user().inventory.add(item.name, item.quantity)

        await bot.send_message(
            self._user().id,
            f'Поздравляю🎉, ты получил достижение "{user_achievement.name}"\n\nЗа это ты получил:\n{reward}',
        )
        await self._user().update_async()

    def get(self, name: str) -> UserAchievement:
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement
        raise AchievementNotFoundError(name)

    def incr_progress(self, key: str, quantity: int = 1):
        if self.is_completed(key.replace("-", " ")):
            return
        if key in self.progress:
            self.progress[key] += quantity
        else:
            self.progress[key] = quantity

        self._user().update()


@dataclass
class UserViolation(SubModel):
    reason: str
    type: Literal["warn", "mute", "ban", "permanent-ban"]
    until_date: Optional[datetime] = None


@dataclass
class DailyGift(SubModel):
    streak: int = 0
    last_claimed_at: Optional[datetime] = None
    next_claimable_at: datetime = field(default_factory=lambda: utcnow() + timedelta(days=1))
    is_claimed: bool = False
    items: dict[str, int] = field(default_factory=dict)


@dataclass
class UserTask(SubModel):
    needed_items: dict[str, int]
    xp: float
    reward: int  # coin
    start_time: datetime = field(default_factory=utcnow)


@dataclass
class UserModel(BaseModel):
    __settings__ = {"collection_name": "users"}
    id: int
    name: str
    lang: str = "ru"
    registered_at: datetime = field(default_factory=utcnow)
    level: int = 1
    coin: int = 0
    xp: float = 0.0
    max_xp: float = calc_xp_for_level(1)
    is_admin: bool = False
    health: int = 100
    mood: int = 100
    hunger: int = 100
    fatigue: int = 100
    luck: int = 1
    last_active_time: datetime = field(default_factory=utcnow)
    accepted_rules: bool = False
    casino_info: CasinoInfo = field(default_factory=CasinoInfo)
    action: Optional[UserAction] = None
    location: Locations = Locations.HOME
    inventory: Inventory = field(default_factory=Inventory)
    notification_status: UserNotificationStatus = field(default_factory=UserNotificationStatus)
    achievements_info: AchievementsInfo = field(default_factory=AchievementsInfo)
    violations: list[UserViolation] = field(default_factory=list)
    task: Optional[UserTask] = None
    max_items_count_in_market: int = 2

    def __post_init__(self):
        self.achievements_info._user = ref(self)  # pylint: disable=W0212

    @property
    def tg_tag(self) -> str:
        return f"<a href='tg://user?id={self.id}'>{self.name}</a>"

    async def new_task(self):
        available_items = [item for item in ITEMS if item.is_task_item]

        items_quantity = random.randint(1, 5)
        items = random.choices(available_items, k=items_quantity)

        task_items: dict[str, int] = {}

        total_price = 0
        for item in items:
            task_items[item.name] = random.randint(2, 10) * self.level
            total_price += random.randint(min(item.task_coin), max(item.task_coin))  # type: ignore

        xp = random.uniform(5.0, float(len(items)))
        reward = int(total_price * 1.5)
        reward += random.randint(0, 100)  # Случайная добавка к награде

        self.task = UserTask(
            task_items,
            xp=xp,
            reward=reward,
        )

    async def _level_up(self, chat_id: Optional[ChatIdType] = None):
        if not chat_id:
            chat_id = self.id

        if self.xp > self.max_xp:
            self.xp -= self.max_xp
        else:
            self.xp = 0.0

        self.level += 1
        self.max_xp = calc_xp_for_level(self.level)

        mess = f"{self.tg_tag} получил новый уровень 🏵"

        box = self.inventory.add_and_get("бокс")
        self.inventory.add("бокс", max(0, box.quantity) + 1)

        await self.update_async()

        builder = InlineKeyboardBuilder()
        buttons: list[InlineKeyboardButton] = []
        btn_data: list[tuple[str, str]] = []

        if self.max_items_count_in_market <= 10:
            btn_data.append(("+1 место в ларьке", "market"))
        if self.level >= 10 and self.luck <= 15:
            btn_data.append(("+1 удача", "luck"))

        for data in btn_data:
            buttons.append(
                InlineKeyboardButton(text=data[0], callback_data=f"levelup {data[1]} {self.id}")
            )

        builder.add(*buttons)
        builder.adjust(1)
        if len(buttons) != 0:
            mess += "\n\nВыбери что хочешь улучшить"

        await bot.send_sticker(chat_id, Stickers.level_up)
        await bot.send_message(chat_id, mess, reply_markup=builder.as_markup())

    async def check_status(self, chat_id: Optional[ChatIdType] = None):
        if not chat_id:
            chat_id = self.id

        if self.xp >= self.max_xp:
            await self._level_up(chat_id)

        attrs = ("health", "mood", "fatigue", "hunger")

        for attr_name in attrs:
            attr: int = getattr(self, attr_name)
            attr = max(0, min(attr, 100))
            setattr(self, attr_name, attr)

    async def check_achievements(self):
        unknown_achievements = set()

        for user_ach in self.achievements_info.achievements:
            try:
                ach = get_achievement(user_ach.name.lower().replace("-", " "))
            except AchievementNotFoundError:
                unknown_achievements.add(user_ach)
                continue

            if ach.check(self):
                await self.achievements_info.award(ach)


@dataclass
class PromoModel(BaseModel):
    __settings__ = {"collection_name": "promos"}

    code: str
    items: dict[str, int]
    usage_count: int = 1
    users: set[ObjectId] = field(default_factory=set)

    @property
    def is_used(self) -> bool:
        return len(self.users) > self.usage_count


# @dataclass
# class MarketItemModel(BaseModel):
#     name: str
#     price: int
#     quantity: int
#     owner_oid: ObjectId
#     usage: Optional[float] = None
#     publishes_ad: datetime = field(default_factory=utcnow)

#     @property
#     def owner(self) -> UserModel:
#         return UserModel.get(oid=self.owner_oid)

#     @property
#     def type(self) -> ItemType:
#         return get_item(self.name).type

#     def __post_init__(self):
#         item = get_item(self.name)
#         if item.type == ItemType.USABLE and self.quantity > 1:
#             raise ValueError("Quantity must be 0 or 1 for items with type `ItemType.USABLE`")
#         if item.type == ItemType.STACKABLE and self.usage is not None:
#             raise ValueError("Usage must be `None` for items with type `ItemType.STACKABLE`")
