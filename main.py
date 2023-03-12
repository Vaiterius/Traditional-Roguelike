import curses

from game.config import *
from game.engine import Engine
from game.dungeon.dungeon import Dungeon
from game.entities import Player
from game.terminal_control import TerminalController


def main(screen: curses.initscr):
    # curses frontend to handle display and input handling.
    terminal_controller = TerminalController(
        screen=screen,
        floor_dimensions=FLOOR_DIMENSIONS
    )

    player = Player(
        x=-1,
        y=-1,
        name="Player",
        char=PLAYER_TILE,
        color="blue",
        hp=100,
        dmg=5
    )

    dungeon = Dungeon(
        player=player,
        wall_char=WALL_TILE,
        floor_char=FLOOR_TILE,
        num_floors=NUM_FLOORS,
        max_entities_per_room=MAX_ENTITIES_PER_ROOM,
        floor_dimensions=FLOOR_DIMENSIONS,
        min_max_rooms=MIN_MAX_ROOMS,
        min_max_room_width=MIN_MAX_ROOM_WIDTH,
        min_max_room_height=MIN_MAX_ROOM_HEIGHT
    )

    engine = Engine(screen, player, dungeon, terminal_controller)
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
