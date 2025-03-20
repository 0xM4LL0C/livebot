from helpers.cache import cached


@cached
def calc_xp_for_level(level: int) -> int:
    return 5 * level + 50 * level + 100
