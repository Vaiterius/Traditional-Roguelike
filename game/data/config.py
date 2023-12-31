# Numerical configurations.
MAX_FOV_DISTANCE: int = 8
NUM_FLOORS: int = 5
MAX_ENEMIES_PER_FLOOR = 3
MAX_ITEMS_PER_FLOOR = 15
FLOOR_DIMENSIONS: tuple[int] = (80, 23)
MIN_MAX_ROOMS: tuple[int] = (6, 9)  # Must have at least 2 rooms.
MIN_MAX_ROOM_WIDTH: tuple[int] = (12, 18)
MIN_MAX_ROOM_HEIGHT: tuple[int] = (4, 6)

# Tile representations.
FLOOR_TILE: str = '.'
WALL_TILE: str = '#'
DESCENDING_STAIRCASE_TILE: str = ">"  # Staircases are entities.
ASCENDING_STAIRCASE_TILE: str = "<"

# UI CHARACTERS.
PROGRESS_BAR_FILLED: str = '█'
PROGRESS_BAR_UNFILLED: str = '█'
