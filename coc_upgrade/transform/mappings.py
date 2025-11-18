from typing import Optional

LAB_LEVEL_TO_TH: dict[int, int] = {
    1: 3,
    2: 4,
    3: 5,
    4: 6,
    5: 7,
    6: 8,
    7: 9,
    8: 10,
    9: 11,
    10: 12,
    11: 13,
    12: 14,
    13: 15,
    14: 16,
    15: 17,
    16: 18,
}

HERO_HALL_TO_TH: dict[int, int] = {
    1: 3,
    2: 4,
    3: 5,
    4: 6,
    5: 7,
    6: 8,
    7: 9,
    8: 10,
    9: 11,
    10: 12,
    11: 13,
    12: 14,
    13: 15,
    14: 16,
    15: 17,
    16: 18,
}


def lab_level_to_th(lab_level: Optional[int]) -> int:
    if lab_level is None:
        return 0
    return LAB_LEVEL_TO_TH.get(lab_level, 0)


def hero_hall_to_th(hero_hall_level: Optional[int]) -> int:
    if hero_hall_level is None:
        return 0
    return HERO_HALL_TO_TH.get(hero_hall_level, 0)

