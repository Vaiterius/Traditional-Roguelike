from __future__ import annotations

import curses
from math import ceil
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .dungeon.dungeon import Dungeon
    from .entities import Entity, Item
    from .components.component import Inventory
from .entities import Creature, Player
from .color import Color
from .message_log import MessageLog
from .pathfinding import in_player_fov
from .render_order import RenderOrder
from .config import PROGRESS_BAR_FILLED, PROGRESS_BAR_UNFILLED


def get_filled_bar(percent: float, width: int) -> str:
    """Return a filled progress bar as a string of block letters"""
    bar = ""
    num_blocks = ceil(percent * width)
    for _ in range(num_blocks):
        bar += PROGRESS_BAR_FILLED
    
    return bar


def get_unfilled_bar(bar_size: int, width: int) -> str:
    """Return the remaining progress bar space which will be colored red"""
    bar = ""
    num_blocks = width - bar_size
    for _ in range(num_blocks):
        bar += PROGRESS_BAR_UNFILLED
    
    return bar


class TerminalController:
    """Handle graphical output of data and terminal input from the player"""

    def __init__(self,
                 screen: curses.initscr,
                 floor_dimensions: tuple[int, int]):
        self.screen = screen
        self.floor_width, self.floor_height = floor_dimensions
        self.colors = Color()  # Fetch available character tile colors.
        self.message_log = MessageLog()
        
        # Keep track for enemies around sidebar.
        self.enemies_in_fov = []
        
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

        # Create the map window itself.
        window = curses.newwin(MAP_HEIGHT + 2, MAP_WIDTH + 2, 0, 0)
        
        # Display tiles.
        window.erase()
        window.border()
        player_info_temp = f"Dungeon Level {floor.dungeon.current_floor_idx + 1}"
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
            if (  # Filter for live enemies to be displayed in the sidebar.
                isinstance(entity, Creature)
                and not isinstance(entity, Player)
                and entity.render_order != RenderOrder.CORPSE
            ):
                self.enemies_in_fov.append(entity)
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
        
        # Create the message log window itself.
        window = curses.newwin(
            MESSAGE_LOG_HEIGHT, MESSAGE_LOG_WIDTH, self.floor_height + 2, 0)
        
        window.erase()
        window.border()

        window.addstr(0, 2, "MESSAGE LOG")
        cursor = 0
        for i in range(MESSAGE_LOG_HEIGHT - 2, 0, -1):
            message = str(self.message_log.get(cursor))
            window.addstr(i, 2, message)  # TODO color code the messages.
            cursor += 1
            if cursor > self.message_log.size() - 1:
                break
        
        window.refresh()
    
    
    def display_sidebar(self, dungeon: Dungeon) -> None:
        """Display sidebar filled with game and player data"""
        player = dungeon.player
        floor = dungeon.current_floor

        SIDEBAR_HEIGHT: int = self.sidebar_height
        SIDEBAR_WIDTH: int = self.sidebar_width
        
        # Create the sidebar window itself.
        window = curses.newwin(
            SIDEBAR_HEIGHT, SIDEBAR_WIDTH, 0, self.map_width + 2)
        
        window.erase()
        
        # PLAYER SECTION #
        PLAYER_SECTION_HEADER = "PLAYER"
        PLAYER_START_X = 0
        PLAYER_HEIGHT = 7
        player_subwindow = window.subwin(
            PLAYER_HEIGHT,
            SIDEBAR_WIDTH,
            PLAYER_START_X,
            self.floor_width + 2)
        player_subwindow.erase()
        player_subwindow.border()
        player_subwindow.addstr(0, 2, PLAYER_SECTION_HEADER)
        player_subwindow.addstr(
            1, 1, player.char, self.colors.get_color(player.color))
        player_subwindow.addstr(1, 3, player.name)

        # Show player health bar.
        player_subwindow.addstr(2, 1, f"HP: {player.hp}/{player.max_hp}")
        hp_percent = player.hp / player.max_hp
        hp_bar: str = get_filled_bar(hp_percent, SIDEBAR_WIDTH - 2)
        player_subwindow.addstr(
            3, 1, hp_bar,
            self.colors.get_color("green"))
        red_hp_bar: str = get_unfilled_bar(len(hp_bar), SIDEBAR_WIDTH - 2)
        player_subwindow.addstr(
            3, 1 + len(hp_bar),
            red_hp_bar,
            self.colors.get_color("red"))

        # Show player magicka bar.
        player_subwindow.addstr(4, 1, f"MP: {player.mp}/{player.max_mp}")
        mp_percent = player.mp / player.max_mp
        mp_bar: str = get_filled_bar(mp_percent, SIDEBAR_WIDTH - 2)
        player_subwindow.addstr(
            5, 1, mp_bar,
            self.colors.get_color("blue"))
        red_mp_bar: str = get_unfilled_bar(len(mp_bar), SIDEBAR_WIDTH - 2)
        player_subwindow.addstr(
            5, 1 + len(mp_bar),
            red_mp_bar,
            self.colors.get_color("red"))


        # ATTRIBUTES SECTION #
        ATTRIBUTES_SECTION_HEADER = "ATTRIBUTES"
        ATTRIBUTES_START_X = PLAYER_START_X + PLAYER_HEIGHT
        ATTRIBUTES_HEIGHT = 6
        attributes_subwindow = window.subwin(
            ATTRIBUTES_HEIGHT,
            SIDEBAR_WIDTH,
            ATTRIBUTES_START_X,
            self.floor_width + 2)
        attributes_subwindow.erase()
        attributes_subwindow.border()
        attributes_subwindow.addstr(0, 2, ATTRIBUTES_SECTION_HEADER)
        attributes_subwindow.addstr(1, 1, f"STR: {player.str}")
        attributes_subwindow.addstr(2, 1, f"AGI: {player.agi}")
        attributes_subwindow.addstr(3, 1, f"CON: {player.con}")
        attributes_subwindow.addstr(4, 1, f"WIS: {player.wis}")


        # STANDING ON SECTION #
        STANDING_ON_SECTION_HEADER = "STANDING ON"
        STANDING_ON_START_X = ATTRIBUTES_START_X + ATTRIBUTES_HEIGHT
        STANDING_ON_HEIGHT = 6
        standing_on_subwindow = window.subwin(
            STANDING_ON_HEIGHT,
            SIDEBAR_WIDTH,
            STANDING_ON_START_X,
            self.floor_width + 2)
        standing_on_subwindow.erase()
        standing_on_subwindow.border()
        standing_on_subwindow.addstr(0, 2, STANDING_ON_SECTION_HEADER)
        
        # Display non-blocking entities that player is current on the tile of.
        # Filter for same tile as player but do not show player.
        entities: list[Entity] = list(filter(
            lambda entity: entity.x == player.x \
                   and entity.y == player.y \
                   and not isinstance(entity, Player),
            floor.entities))
        # Can only show 3 entities at a time.
        entity_iter: int = 1
        displayable_entities: list[Entity] = entities[:3]
        for entity in displayable_entities:
            # Display entity name.
            standing_on_subwindow.addstr(
                entity_iter, 1, f"{entity.char} {entity.name}",
                self.colors.get_color(entity.color))
            entity_iter += 1
        # Rest of entities don't fit on the sidebar, so count the rest.
        remaining_entities: int = len(entities) - len(displayable_entities)
        if remaining_entities > 0:
            standing_on_subwindow.addstr(
                4, 1, f"   and {remaining_entities} more...")


        # ENEMIES AROUND SECTION #
        ENEMIES_AROUND_SECTION_HEADER = "ENEMIES AROUND"
        ENEMIES_AROUND_START_X = STANDING_ON_START_X + STANDING_ON_HEIGHT
        ENEMIES_AROUND_HEIGHT = 11
        enemies_around_subwindow = window.subwin(
            ENEMIES_AROUND_HEIGHT,
            SIDEBAR_WIDTH,
            ENEMIES_AROUND_START_X,
            self.floor_width + 2)
        enemies_around_subwindow.erase()
        enemies_around_subwindow.border()
        enemies_around_subwindow.addstr(0, 2, ENEMIES_AROUND_SECTION_HEADER)

        # Display surrounding enemies and their health bars.
        displayable_enemies_in_fov: list[Creature] = self.enemies_in_fov[:4]
        # Can only show 4 enemies at a time.
        enemy_iter: int = 1
        for enemy in displayable_enemies_in_fov:
            hp_percent = enemy.hp / enemy.max_hp
            enemies_around_subwindow.addstr(
            # Display enemy name.
            enemy_iter, 1, f"{enemy.char} {enemy.name}",
            self.colors.get_color(enemy.color))
            
            # Display enemy healthbar.
            enemy_hp_bar: str = get_filled_bar(hp_percent, SIDEBAR_WIDTH - 2)
            enemies_around_subwindow.addstr(
                enemy_iter + 1, 1,
                enemy_hp_bar,
                self.colors.get_color("green"))
            red_enemy_hp_bar: str = get_unfilled_bar(
                len(enemy_hp_bar), SIDEBAR_WIDTH - 2)
            enemies_around_subwindow.addstr(
                enemy_iter + 1, 1 + len(enemy_hp_bar),
                red_enemy_hp_bar,
                self.colors.get_color("red"))
            enemy_iter += 2

        # Rest of enemies don't fit on the sidebar, so count the rest.
        remaining_enemies_in_fov: int = len(self.enemies_in_fov) \
                                        - len(displayable_enemies_in_fov)
        if remaining_enemies_in_fov > 0:
            enemies_around_subwindow.addstr(
                9, 1, f"    and {remaining_enemies_in_fov} more...")


        # HELP SECTION #
        HELP_SECTION_HEADER = "HELP"
        HELP_START_X = ENEMIES_AROUND_START_X + ENEMIES_AROUND_HEIGHT
        HELP_HEIGHT = 5
        help_subwindow = window.subwin(
            HELP_HEIGHT,
            SIDEBAR_WIDTH,
            HELP_START_X,
            self.floor_width + 2)
        help_subwindow.erase()
        help_subwindow.border()
        help_subwindow.addstr(0, 2, HELP_SECTION_HEADER)
        help_subwindow.addstr(1, 1, "Press:")
        help_subwindow.addstr(2, 1, "'?' for commands list")
        help_subwindow.addstr(3, 1, "'/' for symbol legend")
        
        window.refresh()
        player_subwindow.refresh()
        attributes_subwindow.refresh()
        standing_on_subwindow.refresh()
        enemies_around_subwindow.refresh()
        help_subwindow.refresh()


    def display_inventory(self,
                          inventory: Inventory,
                          cursor_index_pos: int) -> int:
        """Display the inventory menu for player to select through"""
        INVENTORY_HEIGHT: int = inventory.max_slots + 2
        INVENTORY_WIDTH: int = 40

        # Topleft corner where the new window will be positioned at.
        origin_x = (self.game_height // 2) - (INVENTORY_HEIGHT // 2)
        origin_y = (self.game_width // 2) - (INVENTORY_WIDTH // 2)

        # Create the inventory window itself.
        window = curses.newwin(
            INVENTORY_HEIGHT, INVENTORY_WIDTH, origin_x, origin_y)
        
        HEADER_TEXT = "INVENTORY"
        
        window.erase()
        window.border()
        window.addstr(
            0, (INVENTORY_WIDTH // 2) - (len(HEADER_TEXT) // 2), HEADER_TEXT)

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
                window.addstr(
                    index, 4,
                    SINGLE_DIGIT_ADDON + str(index) + ") " + item.name)
            else:
                window.addstr(
                    index, 4, SINGLE_DIGIT_ADDON + str(index) + ") N/A")
        
        window.refresh()
        
        return cursor_index_pos
    

    def ensure_right_terminal_size(self):
        """Ensure terminal has space for game output"""
        x, y = self.screen.getmaxyx()
        message = "TERMINAL TOO SMALL"
        submessage = f"resize to at least ({self.game_height + 1}," \
                     f"{self.game_width + 1})"
        message_ypos = y // 2 - (len(message) // 2)
        submessage_ypos = y // 2 - (len(submessage) // 2)
        
        # Complain if user resizes terminal too small.
        while x <= self.game_height or y <= self.game_width:
            self.screen.erase()
            self.screen.addstr(x // 2, message_ypos, message)
            self.screen.addstr((x // 2) + 1, submessage_ypos, submessage)

            # Update terminal size.
            x, y = self.screen.getmaxyx()
            message_ypos = y // 2 - (len(message) // 2)
            submessage_ypos = y // 2 - (len(submessage) // 2)
            self.screen.refresh()
    

    def get_input(self):
        """Retrieve player input"""
        return self.screen.getkey()

