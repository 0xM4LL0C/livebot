from typing import Final

from helpers.datatypes import Achievement


ACHIEVEMENTS: Final[list[Achievement]] = [
    Achievement(
        name="работяга",
        emoji="💼",
        desc="поработай 10 раз",
        need=10,
        key="работяга",
        reward={
            "бабло": 10_000,
        },
    ),
    Achievement(
        name="бродяга",
        emoji="🚶",
        desc="погуляй 10 раз",
        need=10,
        key="бродяга",
        reward={
            "бабло": 10_000,
        },
    ),
]
