from typing import Any

from ...item_types import WeaponType

# TODO split into ranged and melee weapons, with ranged having a range field.
weapons: list[dict[str, Any]] = [
    {
        "name": "Training Sword",
        "desc": "Used on training dummies and sparring buddies. Made of wood.",
        "char": ")",
        "color": "brown",
        "type": WeaponType.SWORD,
        "dmg": 1,
        "stat_bonuses": {
            "power": 0,
            "agility": 2,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 5
    },
    {
        "name": "Arming Sword",
        "desc": "Standard issue infantry sword. Iron and very basic.",
        "char": ")",
        "color": "white",
        "type": WeaponType.SWORD,
        "dmg": 5,
        "stat_bonuses": {
            "power": 0,
            "agility": 2,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 40
    },
    {
        "name": "Steel Broadsword",
        "desc": "Not your typical grunt sword. Tempered steel and comfortable grip.",
        "char": ")",
        "color": "grey",
        "type": WeaponType.SWORD,
        "dmg": 6,
        "stat_bonuses": {
            "power": 0,
            "agility": 2,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 30
    },
    {
        "name": "Mercenary Falchion",
        "desc": "...",
        "char": ")",
        "color": "shrouded_grey",
        "type": WeaponType.SWORD,
        "dmg": 6,
        "stat_bonuses": {
            "power": 0,
            "agility": 1,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 35
    },
    {
        "name": "Samurai Katana",
        "desc": "...",
        "char": ")",
        "color": "grey",
        "type": WeaponType.SWORD,
        "dmg": 7,
        "stat_bonuses": {
            "power": 0,
            "agility": 3,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 15
    },
    {
        "name": "Berserker's Seax",
        "desc": "...",
        "char": ")",
        "color": "off_white",
        "type": WeaponType.SWORD,
        "dmg": 8,
        "stat_bonuses": {
            "power": 0,
            "agility": 1,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 10
    },
]
