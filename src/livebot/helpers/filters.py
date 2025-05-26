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
        # First step: separate command with arguments
        # "/command@mention arg1 arg2" -> "/command@mention", ["arg1 arg2"]
        try:
            full_command, *args = text.split(maxsplit=1)
        except ValueError:
            raise CommandException("not enough values to unpack")

        command, _, mention = full_command.partition("@")

        return CommandObject(
            prefix=self.prefix,
            command=command,
            mention=mention or None,
            args=args[0] if args else None,
        )
