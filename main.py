import curses

from game.config import *
from game.render_order import RenderOrder
from game.engine import Engine
from game.dungeon.dungeon import Dungeon
from game.entities import Player, Item
from game.terminal_control import TerminalController
from game.components.component import Inventory
from game.message_log import MessageLog


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
        render_order=RenderOrder.CREATURE,
        hp=500,
        mp=500,
        dmg=5
    )
    player.add_component("inventory", Inventory(num_slots=16))
    test_item_1 = Item(-1, -1, "test_item_1", "?", "default", RenderOrder.ITEM, False)
    test_item_2 = Item(-1, -1, "test_item_2", "?", "default", RenderOrder.ITEM, False)
    test_item_3 = Item(-1, -1, "test_item_3", "?", "default", RenderOrder.ITEM, False)
    player.inventory.add_items([test_item_1, test_item_2, test_item_3])

    dungeon = Dungeon(
        player=player,
        num_floors=NUM_FLOORS,
        max_entities_per_room=MAX_ENTITIES_PER_ROOM,
        floor_dimensions=FLOOR_DIMENSIONS,
        min_max_rooms=MIN_MAX_ROOMS,
        min_max_room_width=MIN_MAX_ROOM_WIDTH,
        min_max_room_height=MIN_MAX_ROOM_HEIGHT
    )

    engine = Engine(screen, player, dungeon, MessageLog(), terminal_controller)
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
