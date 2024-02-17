"""Script that counts content of the game such as number of items and enemies.

`python3 -m tests.count_object_data`
"""
from typing import Iterable

from game.data.creatures import enemies
from game.data.items.weapons import weapons
from game.data.items.armor import armor
from game.data.items.potions import restoration_potions
from game.data.items.scrolls import scrolls


def count_objects(container: Iterable) -> int:
    return len(container)


print("GAME OBJECT DATA")
print("------------------")
print(f"# of enemies: {count_objects(enemies)}")
print(f"# of weapons: {count_objects(weapons)}")
print(f"# of armor: {count_objects(armor)}")
print(f"# of potions: {count_objects(restoration_potions)}")
print(f"# of scrolls: {count_objects(scrolls)}")
