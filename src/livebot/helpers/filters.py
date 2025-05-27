from aiogram.filters import Command, CommandObject
from aiogram.filters.command import CommandException, CommandPatternType


class CustomCommandFilter(Command):
    def __init__(self, *values: CommandPatternType, **kwargs):
        super().__init__(
            *values,
            prefix="",
            **kwargs,
        )

    def extract_command(self, text: str) -> CommandObject:
        try:
            full_command, *args = text.split(maxsplit=1)
        except ValueError:
            raise CommandException("not enough values to unpack")  # pylint: disable=W0707

        command, _, mention = full_command.partition("@")

        return CommandObject(
            prefix=self.prefix,
            command=command,
            mention=mention or None,
            args=args[0] if args else None,
        )
