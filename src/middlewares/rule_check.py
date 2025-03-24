from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from consts import TELEGRAM_ID
from database.models import UserModel
from helpers.utils import quick_markup


async def send_rules_message(message: Message, user: UserModel):
    mess = f"{user.tg_tag}, перед тем как использовать бота, ты должен прочитать правила"
    markup = quick_markup(
        {
            "Читать": {"url": "https://hamletsargsyan.github.io/livebot/rules"},
            "Я прочитал и полностью согласен с правилами": {
                "callback_data": f"accept_rules {user.id}"
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
