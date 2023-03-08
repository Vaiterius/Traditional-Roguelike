# Numerical configurations.
NUM_FLOORS: int = 5
MAX_ENTITIES_PER_ROOM = 3
FLOOR_DIMENSIONS: tuple[int] = (100, 25)
MIN_MAX_ROOMS: tuple[int] = (5, 10)
MIN_MAX_ROOM_WIDTH: tuple[int] = (14, 19)
MIN_MAX_ROOM_HEIGHT: tuple[int] = (4, 7)

# Tile representations.
PLAYER_TILE: str = '@'
FLOOR_TILE: str = '.'
WALL_TILE: str = '#'

# Enemy data.
enemies: dict[str, dict] = {
    "ghoul": {
        "name": "Ghoul",
        "char": 'g',
        "color": "red",
        "hp": 65,
        "dmg": 6,
        "spawn_chance": 33  # out of 100, relative weight percentage
    },
    "giant_rat": {
        "name": "Giant Rat",
        "char": "r",
        "color": "black",
        "hp": 35,
        "dmg": 3,
        "spawn_chance": 45
    },
    "vampire": {
        "name": "Vampire",
        "char": "V",
        "color": "magenta",
        "hp": 75,
        "dmg": 6,
        "spawn_chance": 25
    },
    "troll": {
        "name": "Troll",
        "char": "t",
        "color": "green",
        "hp": 40,
        "dmg": 7,
        "spawn_chance": 40
    },
    "wraith": {
        "name": "Wraith",
        "char": "w",
        "color": "cyan",
        "hp": 30,
        "dmg": 8,
        "spawn_chance": 25
    },
    "giant_spider": {
        "name": "Giant Spider",
        "char": "s",
        "color": "black",
        "hp": 25,
        "dmg": 7,
        "spawn_chance": 20
    },
    "imp": {
        "name": "Imp",
        "char": "i",
        "color": "green",
        "hp": 15,
        "dmg": 5,
        "spawn_chance": 45
    },
    "jhermayne": {
        "name": "Jhermayne",
        "char": "J",
        "color": "yellow",
        "hp": 1,
        "dmg": 99,
        "spawn_chance": 1
    },
}
