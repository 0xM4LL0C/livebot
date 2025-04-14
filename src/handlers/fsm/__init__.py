from aiogram import Router

from handlers.fsm.market import router as market_router


router = Router()
router.include_routers(
    market_router,
)
