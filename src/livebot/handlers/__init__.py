from aiogram import F, Router
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.fsm.scene import SceneRegistry
from aiogram.types import ErrorEvent, Message

from livebot.config import logger
from livebot.handlers.admin import router as admin_router
from livebot.handlers.callback import router as callback_router
from livebot.handlers.message import router as message_router
from livebot.handlers.scenes import router as scenes_router
from livebot.handlers.scenes.market import (
    AddMarketItemFinalScene,
    AddMarketItemMainScene,
    AddMarketItemSelectPriceScene,
    AddMarketItemSelectQuantityScene,
)
from livebot.helpers.localization import t


router = Router()

router.include_routers(
    callback_router,
    admin_router,
    message_router,
    scenes_router,
)

registry = SceneRegistry(router)
registry.add(
    AddMarketItemMainScene,
    AddMarketItemSelectQuantityScene,
    AddMarketItemFinalScene,
    AddMarketItemSelectPriceScene,
)


@router.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    await message.answer(t("error-while-handling-update"))
    logger.critical(f"Error while handling update: {event.exception}")
    raise event.exception
