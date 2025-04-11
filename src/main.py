from cli import ARGS  # isort: skip

import asyncio
from argparse import Namespace

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from tinylogging import Level

from config import aiogram_logger, bot, config, logger
from database.models import UserModel
from handlers import router
from helpers.exceptions import NoResult
from middlewares import middlewares
from tasks import run_tasks


dp = Dispatcher(state_storage=RedisStorage.from_url(config.redis.url))
dp.include_router(router)


def init_middlewares():
    logger.debug("Инициализация мидлваров")  # cspell: disable-line
    for middleware in middlewares:
        dp.message.middleware(middleware())


async def init_bot_commands():
    commands = [
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="daily_gift", description="Ежедневный подарок"),
        BotCommand(command="home", description="Дом"),
        BotCommand(command="inventory", description="Инвентарь"),
        BotCommand(command="quest", description="Квест"),
        BotCommand(command="craft", description="Верстак"),
        BotCommand(command="market", description="Рынок"),
        BotCommand(command="use", description="Юз предметов"),
        BotCommand(command="exchanger", description="Обменник"),
        BotCommand(command="transfer", description="Перекидка предметов"),
        BotCommand(command="shop", description="Магазин"),
        BotCommand(command="achievements", description="Достижения"),
        BotCommand(command="weather", description="Погода"),
        BotCommand(command="casino", description="Казино"),
        BotCommand(command="top", description="Топ"),
        BotCommand(command="ref", description="Реферальная система"),
        BotCommand(command="stats", description="Статистика"),
        BotCommand(command="help", description="Помощь"),
    ]

    await bot.set_my_commands(commands)


async def init_bot_admins():
    for uid in config.general.owners:
        try:
            user = await UserModel.get_async(id=uid)
        except NoResult:
            continue

        user.is_admin = True
        await user.update_async()


async def main(args: Namespace) -> None:
    logger.info("bot started")

    if args.debug or config.general.debug:
        config.general.debug = True
        logger.level = Level.DEBUG
        aiogram_logger.setLevel(10)  # debug
        logger.warning("bot running in debug mode")
    else:
        aiogram_logger.setLevel(30)  # warning

    for handler in logger.handlers:
        handler.level = logger.level

    await init_bot_admins()
    await init_bot_commands()
    init_middlewares()

    if not args.without_tasks:
        run_tasks()

    await dp.start_polling(bot, handle_signals=False)


if __name__ == "__main__":
    try:
        asyncio.run(main(ARGS))
    except KeyboardInterrupt:
        logger.info("bot stopped")
