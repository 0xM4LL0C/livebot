from helpers.cache import cached


@cached
def calc_xp_for_level(level: int) -> float:
    return float(5 * level + 50 * level + 100)
