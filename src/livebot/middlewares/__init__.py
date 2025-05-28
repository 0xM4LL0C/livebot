from typing import Type

from aiogram import BaseMiddleware

from livebot.middlewares.actives import ActiveMiddleware
from livebot.middlewares.register import RegisterMiddleware
from livebot.middlewares.rule_check import RuleCheckMiddleware


middlewares: list[Type[BaseMiddleware]] = [
    RegisterMiddleware,
    RuleCheckMiddleware,
    ActiveMiddleware,
]

__all__ = ["middlewares"]
