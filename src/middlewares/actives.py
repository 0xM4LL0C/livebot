from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from consts import TELEGRAM_ID
from database.models import UserModel
from helpers.datetime_utils import utcnow


class ActiveMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        result = await handler(event, data)
        if isinstance(event, (Message, CallbackQuery)):
            if event.from_user.id == TELEGRAM_ID or event.from_user.is_bot:
                return

            user_id = event.from_user.id
            user = await UserModel.get_async(id=user_id)

            if (utcnow() - user.last_active_time).days >= 1:
                user.achievements_info.incr_progress("новичок")
                user.achievements_info.incr_progress("олд")

            user.last_active_time = utcnow()
            await user.update_async()

            return result
