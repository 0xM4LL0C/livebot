from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from livebot.consts import TELEGRAM_ID
from livebot.database.models import UserModel
from livebot.helpers.callback_factory import RulesCallback
from livebot.helpers.utils import quick_markup


async def send_rules_message(message: Message, user: UserModel):
    mess = f"{user.tg_tag}, перед тем как использовать бота, ты должен прочитать правила"
    markup = quick_markup(
        {
            "Читать": {"url": "https://0xM4LL0C.github.io/livebot/rules"},
            "Я прочитал и полностью согласен с правилами": {
                "callback_data": RulesCallback(user_id=user.id)
            },
        },
    )

    await message.answer(mess, reply_markup=markup)


class RuleCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        if not isinstance(event, (Message, CallbackQuery)):
            return
        if event.from_user.id == TELEGRAM_ID or event.from_user.is_bot:
            return

        user = await UserModel.get_async(id=event.from_user.id)

        if user.accepted_rules:
            return await handler(event, data)

        message: Message
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message  # type: ignore
        else:
            return

        await send_rules_message(message, user)
