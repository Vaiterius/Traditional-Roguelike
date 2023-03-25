# Numerical configurations.
NUM_FLOORS: int = 5
MAX_ENTITIES_PER_ROOM = 3
FLOOR_DIMENSIONS: tuple[int] = (80, 23)
MIN_MAX_ROOMS: tuple[int] = (5, 10)
MIN_MAX_ROOM_WIDTH: tuple[int] = (14, 19)
MIN_MAX_ROOM_HEIGHT: tuple[int] = (4, 7)

# Tile representations.
PLAYER_TILE: str = '@'
FLOOR_TILE: str = '.'
WALL_TILE: str = '#'
DESCENDING_STAIRCASE_TILE: str = ">"  # Staircases are entities.
ASCENDING_STAIRCASE_TILE: str = "<"

# UI CHARACTERS.
PROGRESS_BAR_FILLED: str = '█'
PROGRESS_BAR_UNFILLED: str = '█'
