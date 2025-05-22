from livebot.data.achievements.achievements import ACHIEVEMENTS
from livebot.datatypes import Achievement
from livebot.helpers.cache import cached
from livebot.helpers.exceptions import AchievementNotFoundError


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
