from enum import Enum, auto


class ArmorType(Enum):
    HEAD = auto()
    TORSO = auto()
    LEGS = auto()


class WeaponType(Enum):
    SWORD = auto()
    STAFF = auto()


class ProjectileType(Enum):
    LIGHTNING = auto()
    FLAME = auto()
    HEALING = auto()
    RIZZ = auto()
    CONFUSION = auto()


class PotionType(Enum):
    HEALTH = auto()
    MAGICKA = auto()
    POWER = auto()
    AGILITY = auto()
    VITALITY = auto()
    SAGE = auto()

