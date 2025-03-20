import logging
from typing import Final

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import LinkPreviewOptions
from tinylogging import Level, Logger, LoggingAdapterHandler

from config_types import Config

config: Final = Config.from_file("config.toml")


logger = Logger("Bot", Level.DEBUG if config.general.debug else Level.INFO)

# logger.handlers.add(
#     TelegramHandler(
#         chat_id=config.telegram.log_chat_id,
#         token=config.telegram.token,
#         message_thread_id=config.telegram.log_thread_id,
#         formatter=TelegramFormatter(),
#     )
# )

aiogram_logger = logging.getLogger("aiogram")
aiogram_logger.handlers = []

aiogram_logger.setLevel(logger.level.name.upper())

for handler in logger.handlers:
    aiogram_logger.handlers.append(LoggingAdapterHandler(handler))

bot: Final = Bot(
    token=config.telegram.token,
    default=DefaultBotProperties(
        parse_mode="html",
        allow_sending_without_reply=True,
        link_preview=LinkPreviewOptions(
            is_disabled=True,
        ),
    ),
)
