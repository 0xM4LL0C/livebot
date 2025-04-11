from argparse import ArgumentParser, Namespace
from typing import Final


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Запуск в режиме отладки")
    parser.add_argument("--without-tasks", action="store_true", help="Запуск без задач")

    return parser.parse_args()


ARGS: Final[Namespace] = parse_args()
