from aiogram import F, Router
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from config import logger
from handlers.admin import router as admin_router
from handlers.callback import router as callback_router
from handlers.fsm import router as fms_router
from handlers.message import router as message_router
from helpers.localization import t


router = Router()

router.include_routers(
    callback_router,
    admin_router,
    message_router,
    fms_router,
)


@router.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    await message.answer(t("error-while-handling-update"))
    logger.critical(f"Error while handling update: {event.exception}")
    raise event.exception
