from typing import Any

from ...armor_types import ArmorType

armor: dict[str, dict[str, Any]] = {
    "leather_cap": {
        "name": "Leather Cap",
        "desc": "...",
        "char": "[",
        "color": "white",
        "type": ArmorType.HEAD,
        "dmg_reduct": 4,
        "coverage": 5,
        "stat_bonuses": {
            "power": -1,
            "agility": 1,
            "vitality": 0,
            "sage": 0,
        }
    },
    "leather_chestpiece": {
        "name": "Leather Chestpiece",
        "desc": "...",
        "char": "[",
        "color": "white",
        "type": ArmorType.TORSO,
        "dmg_reduct": "9",
        "coverage": 30,
        "stat_bonuses": {
            "power": -1,
            "agility": 1,
            "vitality": 0,
            "sage": 0,
        }
    },
    "leather_trousers": {
        "name": "Leather Trousers",
        "desc": "...",
        "char": "[",
        "color": "white",
        "type": ArmorType.LEG,
        "dmg_reduct": 7,
        "coverage": 25,
        "stat_bonuses": {
            "power": -1,
            "agility": 1,
            "vitality": 0,
            "sage": 0,
        }
    },
}
