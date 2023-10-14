from typing import Any

from ...item_types import PotionType

restoration_potions: dict[str, dict[str, Any]] = {
    "potion_of_restore_health": {
        "name": "Potion of Restore Health",
        "desc": "...",
        "char": '!',
        "color": "white",
        "type": PotionType.HEALTH,
        "yield": 10,
        "spawn_chance": 50
    },
    "potion_of_restore_magicka": {
        "name": "Potion of Restore Magicka",
        "desc": "...",
        "char": "!",
        "color": "white",
        "type": PotionType.MAGICKA,
        "yield": 10,
        "spawn_chance": 50
    }
}
