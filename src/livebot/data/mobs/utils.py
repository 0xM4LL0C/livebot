import random
from typing import Optional

from livebot.data.mobs.mobs import MOBS
from livebot.database.models import UserModel
from livebot.datatypes import Mob
from livebot.helpers.cache import cached
from livebot.helpers.exceptions import MobNotFoundError


@cached()
def get_mob(name: str) -> Mob:
    for mob in MOBS:
        if mob.name == name:
            return mob
        if mob.translit() == name:
            return mob
    raise MobNotFoundError(name)


def get_random_mob(user: UserModel) -> Optional[Mob]:
    if user.met_mob:
        return
    mob = random.choice(MOBS)
    chance = random.uniform(0.0, 100.0)

    if mob.chance <= chance:
        user.met_mob = True
        return mob
