from __future__ import annotations

import curses
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .entities import Player, Item
    from .components.component import Inventory
from .color import Color
from .message_log import MessageLog
from .pathfinding import in_player_fov


# WINDOW CREATIONS #

def get_new_inventory_window(game_dimensions: tuple[int, int],
                             height: int,
                             width: int) -> curses.newwin:
    """Return a curses window that represents an inventory menu"""
    game_height, game_width = game_dimensions

    # Topleft corner where the window will be positioned at.
    origin_x = (game_height // 2) - (height // 2)
    origin_y = (game_width // 2) - (width // 2)

    return curses.newwin(height, width, origin_x, origin_y)


def get_new_map_view_window(height: int, width: int) -> curses.newwin:
    """Return a curses window that displays the game map"""
    return curses.newwin(height + 2, width + 2, 0, 0)


def get_new_message_log_window(height: int,
                               width: int,
                               map_height: int) -> curses.newwin:
    """Return a curses window that displays in-game message logs"""
    return curses.newwin(height, width, map_height + 2, 0)


def get_new_sidebar_window(height: int,
                           width: int,
                           map_width) -> curses.newwin:
    """Return a curses window that displays sidebar information"""
    return curses.newwin(height, width, 0, map_width + 2)


class TerminalController:
    """Handle graphical output of data and terminal input from the player"""

    def __init__(self,
                 screen: curses.initscr,
                 floor_dimensions: tuple[int, int]):
        self.screen = screen
        self.floor_width, self.floor_height = floor_dimensions
        self.colors = Color()  # Fetching available character tile colors.
        self.message_log = MessageLog()
        
        curses.curs_set(0)  # Hide cursor.
        
        # MAP CONFIG.
        self.map_height: int = self.floor_height
        self.map_width: int = self.floor_width
        
        
        # MESSAGE LOG CONFIG.
        self.message_log_height: int = 10
        self.message_log_width: int = self.map_width + 2
        
        
        # SIDEBAR CONFIG.
        self.sidebar_width: int = 28
        self.sidebar_height: int = self.map_height + self.message_log_height + 2
        
        
        # Entire game window sizes.
        self.game_height = self.map_height + self.message_log_height + 2
        self.game_width = self.map_width + self.sidebar_width + 2


        self.screen.refresh()
    
    
    def display_map(self, floor: Floor, player: Player) -> None:
        """Display the dungeon map itself"""
        MAP_HEIGHT: int = self.map_height
        MAP_WIDTH: int = self.map_width

        window = get_new_map_view_window(MAP_HEIGHT, MAP_WIDTH)
        
        # Display tiles.
        window.erase()
        window.border()
        player_info_temp = f"{player.name} - HP: {player.hp}/{player.max_hp}"
        window.addstr(0, 2, player_info_temp)
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                window.addstr(
                    x + 1, y + 1,
                    floor.tiles[x][y].char,
                    self.colors.get_color(floor.tiles[x][y].color))

        # Display entities (they should be in sorted render order).
        for entity in floor.entities:
            if not in_player_fov(player, entity, floor):
                continue
            window.addstr(
                entity.x + 1,
                entity.y + 1,
                entity.char,
                self.colors.get_color(entity.color)
            )
        
        window.refresh()
    
    
    def display_message_log(self) -> None:
        """Display the in-game message log"""
        MESSAGE_LOG_HEIGHT: int = self.message_log_height
        MESSAGE_LOG_WIDTH: int = self.message_log_width
        
        window = get_new_message_log_window(
            MESSAGE_LOG_HEIGHT, MESSAGE_LOG_WIDTH, self.floor_height)
        
        window.erase()
        window.border()

        window.addstr(0, 2, "MESSAGE LOG")
        cursor = 0
        for i in range(MESSAGE_LOG_HEIGHT - 2, 0, -1):
            message = str(self.message_log.get(cursor))
            window.addstr(i, 2, message)
            cursor += 1
            if cursor > self.message_log.size() - 1:
                break
        
        window.refresh()
    
    
    # TODO design the sidebar
    def display_sidebar(self) -> None:
        """Display sidebar filled with game and player data"""
        SIDEBAR_HEIGHT: int = self.sidebar_height
        SIDEBAR_WIDTH: int = self.sidebar_width
        
        window = get_new_sidebar_window(
            SIDEBAR_HEIGHT, SIDEBAR_WIDTH, self.map_width)
        
        window.erase()
        
        window.border()
        
        window.refresh()


    def display_inventory(self, inventory: Inventory, cursor_index_pos: int) -> int:
        """Display the inventory menu for player to select through"""
        INVENTORY_HEIGHT: int = inventory.max_slots + 2
        INVENTORY_WIDTH: int = 40

        window = get_new_inventory_window(INVENTORY_HEIGHT, INVENTORY_WIDTH)
        
        HEADER_TEXT = "INVENTORY"
        
        window.erase()
        window.border()
        window.addstr(0, (INVENTORY_WIDTH // 2) - (len(HEADER_TEXT) // 2), HEADER_TEXT)

        # Validate cursor position.
        if cursor_index_pos < 0:
            cursor_index_pos = 0
        elif cursor_index_pos > inventory.max_slots - 1:
            cursor_index_pos = inventory.max_slots - 1
            
        window.addstr(cursor_index_pos + 1, 2, ">")

        # Show inventory items.
        SINGLE_DIGIT_ADDON = ' '  # Line up the numbers neatly.
        for index in range(inventory.max_slots):
            item: Optional[Item] = inventory.get_item(index)
            
            index += 1  # Shift from 0-9 numbering to 1-10.
            if index > 9:
                SINGLE_DIGIT_ADDON = ''
            
            if item:
                window.addstr(index, 4, SINGLE_DIGIT_ADDON + str(index) + ") " + item.name)
            else:
                window.addstr(index, 4, SINGLE_DIGIT_ADDON + str(index) + ") N/A")
        
        window.refresh()
        
        return cursor_index_pos
    

    def ensure_right_terminal_size(self):
        """Ensure terminal has space for game output"""
        x, y = self.screen.getmaxyx()
        message = "TERMINAL TOO SMALL"
        message_ypos = y // 2 - (len(message) // 2)
        
        # Complain if user resizes terminal too small.
        while x <= self.game_height or y <= self.game_width:
            self.screen.erase()
            self.screen.addstr(x // 2, message_ypos, message)

            # Update terminal size.
            x, y = self.screen.getmaxyx()
            message_ypos = y // 2 - (len(message) // 2)
            self.screen.refresh()
    

    def get_input(self):
        """Retrieve player input"""
        return self.screen.getkey()

