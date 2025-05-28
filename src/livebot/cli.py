from argparse import ArgumentParser, Namespace
from typing import Final

from livebot.consts import VERSION


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="run in debug mode")
    parser.add_argument("--without-tasks", action="store_true", help="run without tasks")
    parser.add_argument("--no-interactive", action="store_true", help="disable prompts")
    parser.add_argument(
        "-v", "--version", action="version", version=str(VERSION), help="bot version"
    )

    return parser.parse_args()


ARGS: Final[Namespace] = parse_args()
