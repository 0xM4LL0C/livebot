from aiogram.filters import BaseFilter
from aiogram.types import Message


class TextOrCommandFilter(BaseFilter):
    def __init__(self, *aliases: str):
        self.aliases = [a.lower() for a in aliases]

    async def __call__(self, message: Message) -> bool:
        text = message.text.lower()
        return text in self.aliases or (text.startswith("/") and text[1:] in self.aliases)
