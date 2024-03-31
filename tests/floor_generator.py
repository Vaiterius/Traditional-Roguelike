import curses

from game.data.config import *
from game.tile import *
from game.color import Color
from game.rng import RandomNumberGenerator
from game.dungeon.floor import Floor, FloorBuilder


def main(stdscr):
    # Clear screen
    stdscr.clear()
    
    while True:
        stdscr.erase()

        # Refresh for new floor.
        rng = RandomNumberGenerator()
        floor: Floor = (
            FloorBuilder(
                rng=rng, 
                floor_height=FLOOR_HEIGHT,
                floor_width=FLOOR_WIDTH
            )
            .place_walls(tile_type=wall_tile)
            .place_relic_room(tile_type=floor_tile_dim)
            .place_glyphs_room(tile_type=floor_tile)
            .place_rooms(
                num_rooms=rng.randint(MIN_NUM_ROOMS, MAX_NUM_ROOMS),
                min_room_height=MIN_ROOM_HEIGHT,
                max_room_height=MAX_ROOM_HEIGHT,
                min_room_width=MIN_ROOM_WIDTH,
                max_room_width=MAX_ROOM_WIDTH,
                tile_type=floor_tile
            )
            .place_tunnels(tile_type=floor_tile)
        ).build(dungeon=None)

        # Display map.
        for x in range(FLOOR_HEIGHT):
            for y in range(FLOOR_WIDTH):
                stdscr.addstr(
                    x + 1, y + 1,
                    floor.tiles[x][y].char,
                    Color().get_color(floor.tiles[x][y].color)
                )
        
        # Wait for the user to press a key
        key = stdscr.getch()
        
        # Example of how to exit - press 'q' to quit
        if key == ord('q'):
            break

        stdscr.refresh()

# Wrap the main function in curses.wrapper to handle initialization and cleanup
curses.wrapper(main)
