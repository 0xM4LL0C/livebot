import random
from typing import Optional

from data.mobs.mobs import MOBS
from database.models import UserModel
from datatypes import Mob
from helpers.cache import cached
from helpers.exceptions import MobNotFoundError


@cached
def get_mob(name: str) -> Mob:
    for mob in MOBS:
        if mob.name == name:
            return mob
        if mob.translit() == name:
            return mob
    raise MobNotFoundError(name)


def get_random_mob(user: UserModel) -> Optional[Mob]:
    if not user.met_mob:
        return
    mob = random.choice(MOBS)
    chance = random.uniform(0.0, 100.0)

    if mob.chance <= chance:
        user.met_mob = True
        return mob
