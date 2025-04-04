from data.achievements.achievements import ACHIEVEMENTS
from datatypes import Achievement
from helpers.cache import cached
from helpers.exceptions import AchievementNotFoundError


@cached()
def get_achievement(name: str) -> Achievement:
    for achievement in ACHIEVEMENTS:
        if achievement.name == name:
            return achievement
        if name == achievement.translit():
            return achievement
        if name == achievement.key:
            return achievement
    raise AchievementNotFoundError(name)
