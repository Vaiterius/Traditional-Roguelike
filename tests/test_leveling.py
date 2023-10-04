from math import sqrt


def leveling_formula(level: int) -> int:
    return (5 * level) + 5


for i in range(1, 11):
    print(f"Level {i}: {leveling_formula(i)}xp needed to level up")