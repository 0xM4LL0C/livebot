from aiogram import F, Router
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from config import logger
from database.models import UserModel
from handlers.admin import router as admin_router
from handlers.callback import router as callback_router
from handlers.message import router as message_router
from helpers.localization import t

router = Router()

router.include_routers(
    callback_router,
    admin_router,
    message_router,
)


@router.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    user = await UserModel.get_async(id=message.from_user.id)
    await message.answer(t(user.lang, "error-while-handling-update"))
    logger.critical(f"Error while handling update: {event.exception}")
    raise event.exception
