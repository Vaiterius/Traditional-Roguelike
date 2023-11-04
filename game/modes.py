from enum import Enum, auto


class GameMode(Enum):
    """Store different gamemodes a player can start their save with.

    NORMAL - play through a storyline and reach a max floor.
    ENDLESS - play through a dungeon with no limits to number of floors.
    SEEDED_NORMAL - like NORMAL, but generated with an inputted seed.
    SEEDED_ENDLESS - like ENDLESS, but generated with an inputted seed.

    """
    NORMAL = auto()
    ENDLESS = auto()
    SEEDED_NORMAL = auto()
    SEEDED_ENDLESS = auto()


class GameStatus(Enum):
    """
    Keep track whether the game has finished (and how it finished) or not.
    """
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()

