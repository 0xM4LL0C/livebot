import asyncio
import itertools
import sys
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Generator, Iterable, ParamSpec, Self, Sequence, TypeVar

from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.cache import cached

P = ParamSpec("P")
T = TypeVar("T")


@cached
def remove_not_allowed_symbols(text: str) -> str:
    not_allowed_symbols = ["#", "<", ">", "{", "}", '"', "'", "$", "(", ")", "@", "`", "\\"]
    cleaned_text = "".join(char for char in text if char not in not_allowed_symbols)

    return cleaned_text.strip()


@cached
def calc_percentage(part: int, total: int = 100) -> float:
    if total == 0:
        raise ValueError("Общий объем не может быть равен нулю")
    return (part / total) * 100


@cached
def create_progress_bar(percentage: float) -> str:
    if not (0 <= percentage <= 100):  # pylint: disable=superfluous-parens
        raise ValueError("Процент должен быть в диапазоне от 0 до 100.")

    length: int = 10
    filled_length = int(length * percentage // 100)
    empty_length = length - filled_length

    filled_block = "■"
    empty_block = "□"

    progress_bar = filled_block * filled_length + empty_block * empty_length
    return progress_bar


@cached
def quick_markup(
    values: dict[str, dict[str, Any]],
    *,
    sizes: Sequence[int] = (1,),
    repeat: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=text, **kwargs) for text, kwargs in values.items()]
    builder.add(*buttons)
    builder.adjust(*sizes, repeat=repeat)
    return builder.as_markup()


async def antiflood(func: Awaitable[T]) -> T:
    number_retries = 5
    for _ in range(number_retries):
        try:
            return await func
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
    return await func


if sys.version_info >= (3, 12):
    batched = cached(itertools.batched)  # pylint: disable=invalid-name,no-member
else:

    @cached
    def batched(iterable: Iterable[T], n: int) -> Generator[tuple[T, ...], None, None]:
        # https://docs.python.org/3.12/library/itertools.html#itertools.batched
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while batch := tuple(itertools.islice(iterator, n)):
            yield batch


@cached
def pretty_datetime(d: datetime) -> str:
    return d.strftime("%H:%M %d.%m.%Y")


@cached
def get_time_difference_string(d: timedelta) -> str:
    years, days_in_year = divmod(d.days, 365)
    months, days = divmod(days_in_year, 30)
    hours, remainder = divmod(d.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    data = ""
    if years > 0:
        data += f"{years} г. "
    if months > 0:
        data += f"{months} мес. "
    if days > 0:
        data += f"{days} д. "
    if hours > 0:
        data += f"{hours} ч. "
    if minutes > 0:
        data += f"{minutes} м. "

    data += f"{seconds} с. "
    return data


class MessageEditor:
    def __init__(
        self,
        user_message: Message,
        *,
        title: str,
    ):
        self.user_message = user_message
        self.message: Message

        self.title = title
        self._mess = f"<b>{self.title}</b>"
        self.exit_funcs: set[Callable[[], None | Any]] = set()

    async def __aenter__(self) -> Self:
        self.message = await antiflood(self.user_message.reply(self._mess))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for func in self.exit_funcs:
            func()

    async def write(self, new_text: str):
        self._mess = text = f"{self._mess}\n<b>*</b>  {new_text}"
        self.message = await antiflood(self.message.edit_text(text))  # type: ignore


@cached
def pretty_float(num: float) -> str:
    return f"{num:.2f}"
