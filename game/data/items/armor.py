from typing import Any

from ...item_types import ArmorType

armor: list[dict[str, Any]] = [
    ### HEAD ###
    {
        "name": "Leather Coif",
        "desc": "...",
        "char": "[",
        "color": "brown",
        "type": ArmorType.HEAD,
        "dmg_reduct": 4,  # Percent reduced.
        "coverage": 5,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 40
    },
    {
        "name": "Padded cap",
        "desc": "...",
        "char": "[",
        "color": "grey",
        "type": ArmorType.HEAD,
        "dmg_reduct": 5,  # Percent reduced.
        "coverage": 6,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 30
    },
    {
        "name": "Chainmail hood",
        "desc": "...",
        "char": "[",
        "color": "white",
        "type": ArmorType.HEAD,
        "dmg_reduct": 7,  # Percent reduced.
        "coverage": 10,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 25
    },
    {
        "name": "Spangenhelm",
        "desc": "...",
        "char": "[",
        "color": "gold",
        "type": ArmorType.HEAD,
        "dmg_reduct": 9,  # Percent reduced.
        "coverage": 8,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 15
    },

    ### TORSO ###
    {
        "name": "Leather Jerkin",
        "desc": "...",
        "char": "[",
        "color": "red",
        "type": ArmorType.TORSO,
        "dmg_reduct": 10,
        "coverage": 30,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 40
    },
    {
        "name": "Scale Chestpiece",
        "desc": "...",
        "char": "[",
        "color": "gold",
        "type": ArmorType.TORSO,
        "dmg_reduct": 14,
        "coverage": 35,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 30
    },
    {
        "name": "Brigandine",
        "desc": "...",
        "char": "[",
        "color": "red",
        "type": ArmorType.TORSO,
        "dmg_reduct": 18,
        "coverage": 40,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 15
    },

    ### LEGS ###
    {
        "name": "Leather Trousers",
        "desc": "...",
        "char": "[",
        "color": "brown",
        "type": ArmorType.LEGS,
        "dmg_reduct": 7,
        "coverage": 25,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 40
    },
    {
        "name": "Padded Chausses",
        "desc": "...",
        "char": "[",
        "color": "grey",
        "type": ArmorType.LEGS,
        "dmg_reduct": 9,
        "coverage": 25,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 30
    },
    {
        "name": "Plate Greaves",
        "desc": "...",
        "char": "[",
        "color": "white",
        "type": ArmorType.LEGS,
        "dmg_reduct": 11,
        "coverage": 18,
        "stat_bonuses": {
            "power": 0,
            "agility": 0,
            "vitality": 0,
            "sage": 0,
        },
        "spawn_chance": 20
    },
]
