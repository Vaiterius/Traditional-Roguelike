from enum import Enum, auto


class RenderOrder(Enum):
    CORPSE = auto()
    STAIRCASE = auto()
    FURNITURE = auto()
    ITEM = auto()
    CREATURE = auto()

