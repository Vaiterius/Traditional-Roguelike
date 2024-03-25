### NUMERICAL ###
# General.
MAX_FOV_DISTANCE: int = 8

# Floor specs.
NUM_FLOORS: int = 10  # At least 5 or main quest will break.
FLOOR_HEIGHT: int = 23
FLOOR_WIDTH: int = 80
MIN_NUM_ROOMS: int = 6  # At least 2.
MAX_NUM_ROOMS: int = 9  # At least 2.
MIN_ROOM_HEIGHT: int = 4
MAX_ROOM_HEIGHT: int = 6
MIN_ROOM_WIDTH: int = 12
MAX_ROOM_WIDTH: int = 18

# Entities/AI.
MAX_ENEMIES_PER_FLOOR: int = 3
MAX_ITEMS_PER_FLOOR: int = 6
CHANCE_TO_SWITCH_ROOMS: float = 0.03  # Travelling creature to another room.
CHANCE_TO_TAKE_STEP: float = 0.75  # Creature pacing around a room.

### CHARACTER ###
# Tile representations.
FLOOR_TILE: str = '.'
WALL_TILE: str = '#'
DESCENDING_STAIRCASE_TILE: str = ">"  # Staircases are entities.
ASCENDING_STAIRCASE_TILE: str = "<"

# UI CHARACTERS.
PROGRESS_BAR_FILLED: str = '█'
PROGRESS_BAR_UNFILLED: str = '█'
