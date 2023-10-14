from typing import Any

from ...item_types import WeaponType

weapons: dict[str, dict[str, Any]] = {
    "training_sword": {
        "name": "Training Sword",
        "desc": "...",
        "char": ")",
        "color": "white",
        "type": WeaponType.SWORD,
        "dmg": 3,
        "stat_bonuses": {
            "power": 0,
            "agility": 2,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 50
    },
}
