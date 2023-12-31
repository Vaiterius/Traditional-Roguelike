from typing import Any

from ...item_types import WeaponType, StaffType

staves: list[dict[str, Any]] = [
    {
        "name": "Staff of Lightning",
        "desc": "Strike a powerful zap of lightning at your opponents",
        "char": "/",
        "color": "white",
        "type": WeaponType.STAFF,
        "staff_type": StaffType.PROJECTILE,
        "uses": 10,
        "mana_cost": 5,
        "dmg": 10,
        "spawn_chance": 50
    },
    {
        "name": "Staff of Rizz",
        "desc": "Rizz up an opponent to temporarily make them your ally",
        "char": "/",
        "color": "orange",
        "type": WeaponType.STAFF,
        "staff_type": StaffType.RIZZ,
        "uses": 2,
        "mana_cost": 5,
        "dmg": -1,
        "spawn_chance": 50
    }
]
