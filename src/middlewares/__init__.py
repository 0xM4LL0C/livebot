from typing import Type

from aiogram import BaseMiddleware

from .register import RegisterMiddleware


middlewares: list[Type[BaseMiddleware]] = [
    RegisterMiddleware,
]

__all__ = ["middlewares"]
