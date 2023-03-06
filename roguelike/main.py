import curses

import config
from engine import Engine
from dungeon import Dungeon
from entities import Player
from terminal_control import TerminalController


def main(screen):
    # curses frontend to handle display and input handling.
    terminal_controller = TerminalController(screen)

    player = Player(
        x=-1,
        y=-1,
        name="<unnamed>",
        char=config.PLAYER_TILE,
        color="white",
        max_hp=12
    )

    dungeon = Dungeon(
        player=player,
        wall_char=config.WALL_TILE,
        floor_char=config.FLOOR_TILE,
        num_floors=config.NUM_FLOORS,
        floor_dimensions=config.FLOOR_DIMENSIONS,
        min_max_rooms=config.MIN_MAX_ROOMS,
        min_max_room_width=config.MIN_MAX_ROOM_WIDTH,
        min_max_room_height=config.MIN_MAX_ROOM_HEIGHT
    )

    engine = Engine(screen, player, dungeon, terminal_controller)
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
