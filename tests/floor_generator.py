import random
import curses

from game.data.config import *
from game.tile import *
from game.color import Color
from game.rng import RandomNumberGenerator
from game.dungeon.floor import Floor, FloorBuilder
from game.spawner import Spawner

FLOOR_HEIGHT -= 7
FLOOR_WIDTH -= 25


def main(stdscr):
    # Clear screen
    stdscr.clear()

    vertical_first: bool = True
    # rand_seed = random.randint(0, 10000)
    rand_seed = 5509
    rng = RandomNumberGenerator(rand_seed)
    builder: FloorBuilder = get_builder(rng, vertical_first)
    floor: Floor = get_floor(builder)
    
    while True:
        stdscr.erase()

        # Display map.
        for x in range(FLOOR_HEIGHT):
            for y in range(FLOOR_WIDTH):
                stdscr.addstr(
                    x + 1, y + 1,
                    floor.tiles[x][y].char,
                    Color().get_color(floor.tiles[x][y].color)
                )
        
        # Debug info.
        stdscr.addstr(FLOOR_HEIGHT + 1, 1, f"SEED: {rand_seed}")
        
        # Wait for the user to press a key
        key = stdscr.getch()
        
        # Example of how to exit - press 'q' to quit
        if key == ord('q'):
            break
        elif key == ord('r'):
            vertical_first = not vertical_first
            builder = get_builder(RandomNumberGenerator(rand_seed), vertical_first)
            floor = get_floor(builder)
        elif key == ord('\n'):
            rand_seed = random.randint(0, 10000)
            rng = RandomNumberGenerator(rand_seed)
            builder = get_builder(rng, vertical_first)
            floor = get_floor(builder)

        stdscr.refresh()


def get_builder(rng: RandomNumberGenerator, vertical_first: bool) -> FloorBuilder:
    return (
        FloorBuilder(
            rng=rng, 
            floor_height=FLOOR_HEIGHT,
            floor_width=FLOOR_WIDTH
        )
        .place_walls(tile_type=wall_tile)
        .place_relic_room(tile_type=floor_tile_dim)
        .place_glyphs_room(Spawner(rng), tile_type=floor_tile_shrouded)
        .place_rooms(
            # num_rooms=rng.randint(MIN_NUM_ROOMS, MAX_NUM_ROOMS),
            num_rooms=3,
            min_room_height=MIN_ROOM_HEIGHT,
            max_room_height=MAX_ROOM_HEIGHT,
            min_room_width=MIN_ROOM_WIDTH,
            max_room_width=MAX_ROOM_WIDTH,
            tile_type=floor_tile_shrouded
        )
        # .place_glyphs_room(tile_type=floor_tile_shrouded)
        .reverse_rooms()
        .place_tunnels(tile_type=floor_tile, vertical_first=vertical_first)
    )


def get_floor(floor_builder: FloorBuilder) -> Floor:
    return floor_builder.build(dungeon=None)


# Wrap the main function in curses.wrapper to handle initialization and cleanup
curses.wrapper(main)
