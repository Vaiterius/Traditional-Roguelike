from typing import Any

from ...item_types import WeaponType, StaffType

staves: list[dict[str, Any]] = [
    {
        "name": "Staff of Lightning",
        "desc": "Strike a powerful zap of lightning at your opponents",
        "char": "/",
        "color": "white",
        "type": WeaponType.STAFF,
        "staff_type": StaffType.DAMAGE_PROJECTILE,
        "uses": 5,
        "magicka_cost": 5,
        "dmg": 10,
        "spawn_chance": 50
    },
    {
        "name": "Staff of Healing",
        "desc": "Send off an orb of healing to a chosen creature",
        "char": "/",
        "color": "white",
        "type": WeaponType.STAFF,
        "staff_type": StaffType.HEAL_PROJECTILE,
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
        "staff_type": StaffType.EFFECT_PROJECTILE,
        "uses": 2,
        "magicka_cost": 5,
        "dmg": 0,
        "spawn_chance": 50
    }
]
