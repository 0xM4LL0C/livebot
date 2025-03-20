from typing import Final

from datatypes import Achievement, AchievementReward

ACHIEVEMENTS: Final = [
    Achievement(
        name="работяга",
        emoji="💼",
        desc="поработай 10 раз",
        need=10,
        reward=[
            AchievementReward("бабло", 10_000),
        ],
    ),
    Achievement(
        name="бродяга",
        emoji="🚶",
        desc="погуляй 10 раз",
        need=10,
        reward=[
            AchievementReward("бокс", 2),
        ],
    ),
    Achievement(
        name="сонный",
        emoji="💤",
        desc="поспи 15 раз",
        need=15,
        reward=[
            AchievementReward("энергос", 10),
        ],
    ),
    Achievement(
        name="игроман",
        emoji="🎮",
        desc="поиграй 20 раз",
        need=20,
        reward=[
            AchievementReward("бокс", 3),
        ],
    ),
    Achievement(
        name="друзья навеки",
        emoji="🫂",
        desc="пригласи друга по твоей реферальной ссылке и раздели веселье вместе с другом",
        need=1,
        reward=[
            AchievementReward("буст", 2),
        ],
    ),
    Achievement(
        name="продавец",
        emoji="💰",
        desc="продай в рынке 30 предметов",
        need=30,
        reward=[
            AchievementReward("бокс", 5),
        ],
    ),
    Achievement(
        name="богач",
        emoji="💸",
        desc="потрать 200_000 бабла на рынке",
        need=200000,
        reward=[
            AchievementReward("бокс", 5),
            AchievementReward("буст", 2),
        ],
    ),
    Achievement(
        name="кладоискатель",
        emoji="🎁",
        desc="открой 20 сундуков",
        need=20,
        reward=[
            AchievementReward("бокс", 4),
        ],
    ),
    Achievement(
        name="новичок",
        emoji="👋",
        desc="посети игру каждый день на протяжении первой недели",
        need=7,
        reward=[
            AchievementReward("бабло", 5_000),
        ],
    ),
    Achievement(
        name="олд",
        emoji="👨‍🦳",
        desc="оставайся активным игроком в течение целого года",
        need=365,
        reward=[
            AchievementReward("бабло", 20_000),
        ],
    ),
    Achievement(
        name="квестоман",
        emoji="🗺️",
        desc="выполни 50 квестов",
        need=50,
        reward=[
            AchievementReward("бабло", 15_000),
            AchievementReward("буст", 3),
        ],
    ),
]
