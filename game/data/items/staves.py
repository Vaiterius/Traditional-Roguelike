from typing import Any

from ...item_types import WeaponType, ProjectileType

staves: list[dict[str, Any]] = [
    {
        "name": "Staff of Lightning",
        "desc": "Strike a powerful zap of lightning at your opponents",
        "char": "/",
        "color": "white",
        "type": WeaponType.STAFF,
        "staff_type": ProjectileType.LIGHTNING,
        "uses": 5,
        "magicka_cost": 5,
        "dmg": 10,
        "spawn_chance": 50,
    },
    {
        "name": "Staff of Healing",
        "desc": "Send off an orb of healing to a chosen creature",
        "char": "/",
        "color": "white",
        "type": WeaponType.STAFF,
        "staff_type": ProjectileType.HEALING,
        "uses": 5,
        "magicka_cost": 5,
        "dmg": 0,
        "hp": 8,
        "spawn_chance": 50,
    },
    {
        "name": "Staff of Rizz",
        "desc": "Rizz up an opponent to temporarily make them your ally",
        "char": "/",
        "color": "orange",
        "type": WeaponType.STAFF,
        "staff_type": ProjectileType.RIZZ,
        "uses": 2,
        "magicka_cost": 5,
        "turns_remaining": 50,
        "dmg": 0,
        "spawn_chance": 50,
    },
    {
        "name": "Staff of Confusion",
        "desc": "Cast a web of confusion around their mind, causing them to"
                "stumble and make erratic moves",
        "char": "/",
        "color": "orange",
        "type": WeaponType.STAFF,
        "staff_type": ProjectileType.CONFUSION,
        "uses": 2,
        "magicka_cost": 5,
        "turns_remaining": 10,
        "dmg": 0,
        "spawn_chance": 50,
    }
]
