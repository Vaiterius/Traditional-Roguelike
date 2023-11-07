from typing import Any

from ...item_types import PotionType

restoration_potions: list[dict[str, Any]] = [
    {
        "name": "Potion of Restore Health",
        "desc": "...",
        "char": '!',
        "color": "white",
        "type": PotionType.HEALTH,
        "yield": 10,
        "spawn_chance": 50
    },
    {
        "name": "Potion of Restore Magicka",
        "desc": "...",
        "char": "!",
        "color": "white",
        "type": PotionType.MAGICKA,
        "yield": 10,
        "spawn_chance": 50
    }
]
