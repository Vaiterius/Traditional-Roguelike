from enum import Enum, auto


class GameMode(Enum):
    """Store different gamemodes a player can start their save with. Each can
    optionally be seeded by the player on game setup.

    NORMAL - play through a storyline and reach a max floor.
    ENDLESS - play through a dungeon with no limits to number of floors.

    """
    NORMAL = auto()
    ENDLESS = auto()


class GameStatus(Enum):
    """
    Keep track whether the game has finished (and how it finished) or not.
    """
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()

