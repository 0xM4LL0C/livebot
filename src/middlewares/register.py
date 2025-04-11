import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import logger
from consts import TELEGRAM_ID
from database.models import UserModel
from helpers.cache import ram_cache
from helpers.exceptions import NoResult
from helpers.utils import remove_not_allowed_symbols


async def register_user(message: Message) -> UserModel:
    try:
        return await UserModel.get_async(id=message.from_user.id)
    except NoResult:
        user = UserModel(
            id=message.from_user.id,
            name=remove_not_allowed_symbols(message.from_user.full_name),
        )
        await user.add_async()
        logger.info(f"Новый пользователь: {user.name} ({user.id})")

        return user


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        if isinstance(event, Message):
            if event.from_user.id == TELEGRAM_ID or event.from_user.is_bot:
                return

            if event.text.startswith("/start"):
                user = await UserModel.get_async(id=event.from_user.id)
            else:
                user = await register_user(event)

            if event.reply_to_message:
                await register_user(event.reply_to_message)
        else:
            return

        ev = asyncio.Event()
        ram_cache[f"lock-{user.id}"] = (ev, 0.0)
        try:
            ev.set()
            return await handler(event, data)
        finally:
            ev.clear()
