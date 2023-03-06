import curses

from game.config import *
from game.engine import Engine
from game.dungeon import Dungeon
from game.entities import Player
from game.terminal_control import TerminalController


def main(screen):
    # curses frontend to handle display and input handling.
    terminal_controller = TerminalController(screen)

    player = Player(
        x=-1,
        y=-1,
        name="<unnamed>",
        char=PLAYER_TILE,
        color="white",
        max_hp=12
    )

    dungeon = Dungeon(
        player=player,
        wall_char=WALL_TILE,
        floor_char=FLOOR_TILE,
        num_floors=NUM_FLOORS,
        floor_dimensions=FLOOR_DIMENSIONS,
        min_max_rooms=MIN_MAX_ROOMS,
        min_max_room_width=MIN_MAX_ROOM_WIDTH,
        min_max_room_height=MIN_MAX_ROOM_HEIGHT
    )

    engine = Engine(screen, player, dungeon, terminal_controller)
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
