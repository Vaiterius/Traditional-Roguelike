from .data.config import WALL_TILE, FLOOR_TILE


class Tile:
    """Tile representation for each cell on the map"""
    
    def __init__(self,
                 char: str,
                 color: str,
                 walkable: bool,
                 explored: bool = False):
        self.char = char
        self.color = color
        self.walkable = walkable
        self.explored = explored


# WALLS AND FLOORS #

# Tiles in FOV.
wall_tile = Tile(
    char=WALL_TILE, color="white", walkable=False, explored=True)
floor_tile = Tile(
    char=FLOOR_TILE, color="white", walkable=True, explored=True)

# Tiles explored but not in FOV.
wall_tile_dim = Tile(
    char=WALL_TILE, color="grey", walkable=False, explored=True
)
floor_tile_dim = Tile(
    char=FLOOR_TILE, color="grey", walkable=True, explored=True
)

# Tiles unexplored.
wall_tile_shrouded = Tile(
    char=WALL_TILE, color="black", walkable=False, explored=False)
floor_tile_shrouded = Tile(
    char=FLOOR_TILE, color="black", walkable=True, explored=False)
