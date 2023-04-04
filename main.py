import curses

from game.data.config import *
from game.render_order import RenderOrder
from game.engine import Engine
from game.dungeon.dungeon import Dungeon
from game.spawner import Spawner
from game.entities import Item
from game.terminal_control import TerminalController
from game.components.component import Inventory
from game.message_log import MessageLog


def main(screen: curses.initscr):
    # curses frontend to handle display and input handling.
    terminal_controller = TerminalController(
        screen=screen,
        floor_dimensions=FLOOR_DIMENSIONS
    )
    
    spawner = Spawner()

    player = spawner.get_player_instance()
    player.add_component("inventory", Inventory(num_slots=16))
    # TODO remove test items
    test_item_1 = Item(-1, -1, "test_item_1", "?", "default", RenderOrder.ITEM, False)
    test_item_2 = Item(-1, -1, "test_item_2", "?", "default", RenderOrder.ITEM, False)
    test_item_3 = Item(-1, -1, "test_item_3", "?", "default", RenderOrder.ITEM, False)
    player.inventory.add_items([test_item_1, test_item_2, test_item_3])

    dungeon = Dungeon(
        spawner=spawner,
        num_floors=NUM_FLOORS,
        max_enemies_per_floor=MAX_ENEMIES_PER_FLOOR,
        floor_dimensions=FLOOR_DIMENSIONS,
        min_max_rooms=MIN_MAX_ROOMS,
        min_max_room_width=MIN_MAX_ROOM_WIDTH,
        min_max_room_height=MIN_MAX_ROOM_HEIGHT
    )

    engine = Engine(screen, player, dungeon, MessageLog(), terminal_controller)
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
