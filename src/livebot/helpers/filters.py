from aiogram.filters import BaseFilter, CommandObject
from aiogram.types import Message


class CommandWithoutPrefixFilter(BaseFilter):
    def __init__(self, *commands: str):
        self.commands = [cmd.lower() for cmd in commands]

    async def __call__(self, message: Message) -> bool | dict:
        text = message.text.lower()
        for cmd in self.commands:
            if text == cmd:
                return {"command": CommandObject(command=cmd, args="")}
            if text.startswith(cmd + " "):
                args = text[len(cmd) + 1 :].strip()
                return {"command": CommandObject(command=cmd, args=args)}
        return False
