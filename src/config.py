from datetime import datetime
import os
import sys
import logging
from typing import Final

from dotenv import load_dotenv
import telebot


load_dotenv()

DEBUG = True

TOKEN = os.getenv("BOT_TOKEN", "")
DB_URL = os.getenv("DB_URL", "")
DB_NAME = os.getenv("DB_NAME", "")
MODULES_SRC = os.getenv("MODULES_SRC", "")

if not TOKEN:
    raise ValueError
elif not DB_URL:
    raise ValueError
elif not DB_NAME:
    raise ValueError


bot = telebot.TeleBot(
    TOKEN,
    parse_mode="html",
    skip_pending=True,
    num_threads=10,
    disable_web_page_preview=True,
    use_class_middlewares=True,
)


TELEGRAM_ID: Final = 777000


log_chat_id = "-1002110527910"
log_thread_id = 2

weather_region: Final = "Сыктывкар"

timezone: Final = datetime.utcnow().tzinfo

event_end_time: Final = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone)
event_open: Final = True

channel_id: Final = "-1002081230318"
chat_id: Final = "-1001869913117"

GUIDE_FILE_PATH: Final = "guide.toml"


timezone = datetime.utcnow().tzinfo

bot_owners = [5161392463]  # type: list[int]

logger = logging.Logger("Bot")


class TelegramLogsHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        from helpers.utils import log

        log_entry = self.format(record)
        log(log_entry, record.levelname, record)
        del log


logger.addHandler(TelegramLogsHandler())

formatter = logging.Formatter(
    '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
)

console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

telebot.logger.addHandler(TelegramLogsHandler())
telebot.logger.setLevel(20)
