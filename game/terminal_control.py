from __future__ import annotations

import random
import curses
from math import ceil
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .dungeon.dungeon import Dungeon
    from .entities import Entity
    from .components.base_component import Inventory
    from .message_log import Message, MessageLog
    from .gamestates import MenuOption
    from .save_handling import Save
from .dungeon.floor import FloorBuilder
from .tile import *
from .data.config import *
from .entities import Creature, Player, Item
from .color import Color
from .render_order import RenderOrder
from .data.config import PROGRESS_BAR_FILLED, PROGRESS_BAR_UNFILLED
from .save_handling import fetch_save


# TODO turn progress bar into a class
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
        
        # Keep track for enemies around sidebar.
        self.entities_in_fov = []
        
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

        # Game title setup for main menu.
        file_location = "game/data/title.txt"
        self.title_lines: list[str] = self._get_title_lines(
            file_location=file_location, max_width=(self.game_width // 2)
        )
        self.title_width, self.title_height = self._get_title_dimensions(
            self.title_lines)
        
        self.main_menu_tiles: list[list[Tile]] = \
            self._get_main_menu_map_tiles()


        self.screen.refresh()
    
    
    def display_map(self,
                    floor: Floor,
                    tiles_in_fov: dict[tuple[int, int], Tile]) -> None:
        """Display the dungeon map itself"""
        MAP_HEIGHT: int = self.map_height
        MAP_WIDTH: int = self.map_width

        # Create the map window itself.
        window = curses.newwin(MAP_HEIGHT + 2, MAP_WIDTH + 2, 0, 0)
        
        # Display tiles.
        window.erase()
        window.border()
        dungeon_level = f"DUNGEON LEVEL {floor.dungeon.current_floor_idx + 1}"
        window.addstr(0, 2, f"[ {dungeon_level} ]")
        for pos, tile in floor.explored_tiles.items():
            x, y = pos
            window.addstr(
                x + 1, y + 1, tile.char, self.colors.get_color(tile.color))
        for pos, tile in tiles_in_fov.items():
            x, y = pos
            window.addstr(
                x + 1, y + 1, tile.char, self.colors.get_color(tile.color))

        # Display entities (they should be in sorted render order).
        entities: list[Entity] = []
        for entity in floor.entities:
            if not (entity.x, entity.y) in tiles_in_fov:
                continue
            if (  # Filter non-enemies and non-items.
                (isinstance(entity, Creature)
                or isinstance(entity, Item))
                and (not isinstance(entity, Player)
                and entity.render_order != RenderOrder.CORPSE)
            ):
                self.entities_in_fov.append(entity)
            window.addstr(
                entity.x + 1, entity.y + 1, entity.char,
                self.colors.get_color(entity.color)
            )
            entities.append(entity.name)
        
        window.refresh()
    
    
    def display_message_log(self, message_log: MessageLog) -> None:
        """Display the in-game message log"""
        MESSAGE_LOG_HEIGHT: int = self.message_log_height
        MESSAGE_LOG_WIDTH: int = self.message_log_width
        
        # Create the message log window itself.
        window = curses.newwin(
            MESSAGE_LOG_HEIGHT, MESSAGE_LOG_WIDTH, self.floor_height + 2, 0)
        
        window.erase()
        window.border()

        window.addstr(0, 2, "[ MESSAGE LOG ]")
        cursor = 0
        for i in range(MESSAGE_LOG_HEIGHT - 2, 0, -1):
            message: Message = message_log.get(cursor)
            message_text = str(message)
            color: str = message.color
            window.addstr(i, 2, message_text, self.colors.get_color(color))
            cursor += 1
            if cursor > message_log.size - 1:
                break
        
        window.refresh()
    
    
    def display_sidebar(self, dungeon: Dungeon, player: Player) -> None:
        """Display sidebar filled with game and player data"""
        floor = dungeon.current_floor

        SIDEBAR_HEIGHT: int = self.sidebar_height
        SIDEBAR_WIDTH: int = self.sidebar_width
        
        # Create the sidebar window itself.
        window = curses.newwin(
            SIDEBAR_HEIGHT, SIDEBAR_WIDTH, 0, self.map_width + 2)
        
        window.erase()
        
        # PLAYER SECTION #
        PLAYER_SECTION_HEADER = "[ PLAYER ]"
        PLAYER_START_X = 0
        PLAYER_HEIGHT = 7
        player_subwindow = window.subwin(
            PLAYER_HEIGHT,
            SIDEBAR_WIDTH,
            PLAYER_START_X,
            self.floor_width + 2)
        player_subwindow.erase()
        player_subwindow.border()
        player_header_center_y = self._get_message_center_x(
            PLAYER_SECTION_HEADER, SIDEBAR_WIDTH)
        player_subwindow.addstr(
            0, player_header_center_y, PLAYER_SECTION_HEADER)
        player_subwindow.addstr(
            1, 1, player.char, self.colors.get_color(player.color))
        player_subwindow.addstr(1, 3, player.name)

        # Show player health bar.
        hp, max_hp = player.fighter.health, player.fighter.max_health
        player_subwindow.addstr(2, 1, f"HP: {hp}/{max_hp}")
        hp_percent = hp / max_hp
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
        mp, max_mp = player.fighter.magicka, player.fighter.max_magicka
        player_subwindow.addstr(4, 1, f"MP: {mp}/{max_mp}")
        mp_percent = mp / max_mp
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
        ATTRIBUTES_SECTION_HEADER = "[ ATTRIBUTES ]"
        ATTRIBUTES_START_X = PLAYER_START_X + PLAYER_HEIGHT
        ATTRIBUTES_HEIGHT = 6
        attributes_subwindow = window.subwin(
            ATTRIBUTES_HEIGHT,
            SIDEBAR_WIDTH,
            ATTRIBUTES_START_X,
            self.floor_width + 2)
        attributes_subwindow.erase()
        attributes_subwindow.border()
        attributes_header_center_y = self._get_message_center_x(
            ATTRIBUTES_SECTION_HEADER, SIDEBAR_WIDTH)
        attributes_subwindow.addstr(
            0, attributes_header_center_y, ATTRIBUTES_SECTION_HEADER)
        attributes_subwindow.addstr(1, 1, f"POW: {player.fighter.power}")
        attributes_subwindow.addstr(
            2, 1, f"AGI: {player.fighter.agility}")
        attributes_subwindow.addstr(
            3, 1, f"VIT: {player.fighter.vitality}")
        attributes_subwindow.addstr(4, 1, f"SGE: {player.fighter.sage}")


        # STANDING ON SECTION #
        STANDING_ON_SECTION_HEADER = "[ STANDING ON ]"
        STANDING_ON_START_X = ATTRIBUTES_START_X + ATTRIBUTES_HEIGHT
        STANDING_ON_HEIGHT = 6
        standing_on_subwindow = window.subwin(
            STANDING_ON_HEIGHT,
            SIDEBAR_WIDTH,
            STANDING_ON_START_X,
            self.floor_width + 2)
        standing_on_subwindow.erase()
        standing_on_subwindow.border()
        standing_on_header_center_y = self._get_message_center_x(
            STANDING_ON_SECTION_HEADER, SIDEBAR_WIDTH)
        standing_on_subwindow.addstr(
            0, standing_on_header_center_y - 1, STANDING_ON_SECTION_HEADER)
        
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


        # ENTITIES AROUND SECTION #
        ENTITIES_SECTION_HEADER = "[ ENTITIES ]"
        ENTITIES_START_X = STANDING_ON_START_X + STANDING_ON_HEIGHT
        ENTITIES_HEIGHT = SIDEBAR_HEIGHT - ENTITIES_START_X
        entities_subwindow = window.subwin(
            ENTITIES_HEIGHT,
            SIDEBAR_WIDTH,
            ENTITIES_START_X,
            self.floor_width + 2)
        entities_subwindow.erase()
        entities_subwindow.border()
        entities_header_center_y: int = self._get_message_center_x(
            ENTITIES_SECTION_HEADER, SIDEBAR_WIDTH)
        entities_subwindow.addstr(
            0, entities_header_center_y, ENTITIES_SECTION_HEADER)

        # Display surrounding entities and their health bars.
        max_entities_for_display: int = 6
        displayable_entities_in_fov: list[Creature] = \
            self.entities_in_fov[:max_entities_for_display]
        # Show a certain number of entities at a time.
        entity_iter: int = 1
        for entity in displayable_entities_in_fov:
            entities_subwindow.addstr(
            # Display enemy name.
            entity_iter, 1, f"{entity.char} {entity.name}",
            self.colors.get_color(entity.color))
            
            # Display entity healthbar if they are a creature.
            if isinstance(entity, Creature):
                hp_percent = entity.fighter.health / entity.fighter.max_health
                enemy_hp_bar: str = get_filled_bar(
                    hp_percent, SIDEBAR_WIDTH - 2)
                entities_subwindow.addstr(
                    entity_iter + 1, 1,
                    enemy_hp_bar,
                    self.colors.get_color("green"))
                red_enemy_hp_bar: str = get_unfilled_bar(
                    len(enemy_hp_bar), SIDEBAR_WIDTH - 2)
                entities_subwindow.addstr(
                    entity_iter + 1, 1 + len(enemy_hp_bar),
                    red_enemy_hp_bar,
                    self.colors.get_color("red"))

                entity_iter += 2
                continue

            entity_iter += 1

        # Rest of entities don't fit on the sidebar, so count the rest.
        remaining_entities_in_fov: int = len(self.entities_in_fov) \
                                        - len(displayable_entities_in_fov)
        if remaining_entities_in_fov > 0:
            entities_subwindow.addstr(
                ENTITIES_HEIGHT - 2, 1,
                f"    and {remaining_entities_in_fov} more...")
        
        # Then reset.
        self.entities_in_fov = []


        window.refresh()
        player_subwindow.refresh()
        attributes_subwindow.refresh()
        standing_on_subwindow.refresh()
        entities_subwindow.refresh()
        # help_subwindow.refresh()


    def display_inventory(self,
                          inventory: Inventory,
                          cursor_index: int) -> int:
        """Display the inventory menu for player to select through"""

        # SELECTION MENU WINDOW #
        SELECTION_WINDOW_HEIGHT: int = inventory.max_slots + 3
        SELECTION_WINDOW_WIDTH: int = 28
        # ITEM INFO WINDOW #
        ITEM_INFO_HEIGHT: int = SELECTION_WINDOW_HEIGHT
        ITEM_INFO_WIDTH: int = 38
        
        COMBINED_WIDTH: int = SELECTION_WINDOW_WIDTH + ITEM_INFO_WIDTH

        # Topleft corner point for the selection window.
        selection_window_origin_x: int = (self.game_height // 2) - \
            SELECTION_WINDOW_HEIGHT // 2
        selection_window_origin_y: int = (self.game_width // 2) - \
            COMBINED_WIDTH // 2
        # Topleft corner point for the item info window.
        item_info_window_origin_x: int = (self.game_height // 2) - \
            SELECTION_WINDOW_HEIGHT // 2
        item_info_window_origin_y: int = selection_window_origin_y + \
            SELECTION_WINDOW_WIDTH

        # Create the selection window itself.
        selection_window = curses.newwin(
            SELECTION_WINDOW_HEIGHT, SELECTION_WINDOW_WIDTH,
            selection_window_origin_x, selection_window_origin_y
        )
        # Create the item info window itself.
        item_info_window = curses.newwin(
            ITEM_INFO_HEIGHT, ITEM_INFO_WIDTH,
            item_info_window_origin_x, item_info_window_origin_y
        )
        
        HEADER_TEXT = "INVENTORY"
        
        selection_window.erase()
        selection_window.border()
        item_info_window.erase()
        item_info_window.border()
        selection_window.addstr(0, 2, HEADER_TEXT, curses.A_REVERSE)

        # Validate cursor position.
        if cursor_index < 0:
            cursor_index = 0
        elif cursor_index > inventory.max_slots - 1:
            cursor_index = inventory.max_slots - 1

        # List out inventory items.
        SINGLE_DIGIT_ADDON = ' '  # Line up the numbers neatly.
        for index in range(inventory.max_slots):
            item: Optional[Item] = inventory.get_item(index)
            
            # Shift from 0-9 numbering to 1-10.
            slot_char = chr(97 + index)
            index += 1
            # if index > 9:
            #     SINGLE_DIGIT_ADDON = ''
            
            # Highlight the currently selected index item.
            optional_highlight = curses.A_NORMAL
            if index == cursor_index + 1:
                optional_highlight = curses.A_REVERSE
            
            # Fill the slot value.
            # slot_value: str = SINGLE_DIGIT_ADDON + "(" + str(index) + ") "
            slot_value: str = slot_char + ") "
            if item:
                slot_value += item.name
            else:
                slot_value += "<Empty>"
            
            selection_window.addstr(
                index + 1, 2, slot_value, optional_highlight)
        
        # Display currently-selected item's info.
        selected_item: Optional[Item] = inventory.get_item(cursor_index)
        if selected_item is None:
            item_info_window.addstr(1, 1, "<Empty>")
        else:
            item_info_window.addstr(1, 1, f"Name: {selected_item.name}")
            # TODO Item description.
            # TODO Item stats.
            if selected_item.get_component("consumable"):
                pass
            elif selected_item.get_component("equippable"):
                pass
            item_info_window.addstr(2, 1, "Item info not implemented.")
        
        selection_window.refresh()
        item_info_window.refresh()
        
        return cursor_index
    
    
    def display_saves(self,
                      saves: list[Save],
                      cursor_index: int,
                      title: str) -> int:
        """
        Display a list of savefile names as well as metadata beside it.
        """
        PANEL_HEIGHT: int = self.game_height // 2
        PANEL_WIDTH: int = self.game_width // 3
        
        # Create the slots and metadata panels.
        slots_window = curses.newwin(
            PANEL_HEIGHT, PANEL_WIDTH, 
            (self.game_height // 3) - 2,
            (self.game_width // 2) - PANEL_WIDTH
        )
        metadata_window = curses.newwin(
            PANEL_HEIGHT, PANEL_WIDTH,
            (self.game_height // 3) - 2,
            (self.game_width // 2)
        )
        
        slots_window.erase()
        slots_window.border()
        metadata_window.erase()
        metadata_window.border()
        
        # Clamp cursor index.
        if cursor_index < 0:
            cursor_index = 0
        elif cursor_index > len(saves) - 1:
            cursor_index = len(saves) - 1
        
        # Display save slots on slots panel.
        slots_window.addstr(0, 2, title, curses.A_REVERSE)
        first_item_x: int = 3
        for index, save in enumerate(saves):
            # Reverse foreground/background highlighting.
            highlight_attr: int = curses.A_NORMAL
            if index == cursor_index:
                highlight_attr = curses.A_REVERSE
            
            line_pos: int = index + first_item_x
                
            if save.is_empty:
                slots_window.addstr(
                    line_pos, 3, f"({index + 1}) <Empty>", highlight_attr)
                first_item_x += 1
                continue
            slots_window.addstr(
                line_pos, 3, f"({index + 1}) {save.path}", highlight_attr)
            
            first_item_x += 1
        
        # Button actions on the bottom for deleting and returning.
        delete_msg: str = "[x] delete"
        enter_msg: str = "[enter] select"
        go_back_msg: str = "[bcksp] return"
        slots_window.addstr(PANEL_HEIGHT - 2, 2, delete_msg)
        slots_window.addstr(
            1, PANEL_WIDTH - len(go_back_msg) - 2, go_back_msg)
        slots_window.addstr(
            PANEL_HEIGHT - 2, PANEL_WIDTH - len(go_back_msg) - 2, enter_msg)

        # Display save info on the other panel.
        save: Save = fetch_save(saves, cursor_index)
        
        # Empty slot.
        if save.is_empty:
            metadata_window.addstr(1, 1, "<Empty>")
        
        # Save metadata enumerated here.
        else:
            metadata_window.addstr(1, 1, "PLAYER: ", curses.A_BOLD)
            metadata_window.addstr(1, 9, str(save.data.get('player').name))
            metadata_window.addstr(3, 1, "FLOOR: ", curses.A_BOLD)
            metadata_window.addstr(
                3, 8, str(save.data.get('dungeon').current_floor_idx + 1))

            metadata_window.addstr(5, 1, "CREATED AT:", curses.A_BOLD)
            metadata_window.addstr(6, 1, str(save.metadata.get("created_at")))
            metadata_window.addstr(8, 1, f"LAST_PLAYED:", curses.A_BOLD)
            metadata_window.addstr(9, 1, str(save.metadata.get('last_played')))
        
        slots_window.refresh()
        metadata_window.refresh()
        
        return cursor_index
    
    
    def display_main_menu(self,
                          menu_options: list[MenuOption],
                          cursor_index: int) -> int:
        """Display the menu options for the player"""
        MAIN_MENU_HEIGHT: int = self.game_height
        MAIN_MENU_WIDTH: int = self.game_width
        
        # Create the main menu window itself.
        window = curses.newwin(MAIN_MENU_HEIGHT, MAIN_MENU_WIDTH, 0, 0)
        
        OPTIONS_SUBWIN_HEIGHT: int = 8
        OPTIONS_SUBWIN_WIDTH: int = 28
        OPTIONS_SUBWIN_START_Y: int = 3
        
        # Create a subwindow to box the menu options.
        options_subwindow = window.subwin(
            OPTIONS_SUBWIN_HEIGHT, OPTIONS_SUBWIN_WIDTH,
            (self.game_height // 2) + (self.game_height // 4), 3
        )
        
        window.erase()
        
        # Display the cool map background.
        for x in range(self.game_height - 2):
            for y in range(self.game_width - 2):
                window.addstr(
                    x + 1, y + 1,
                    self.main_menu_tiles[x][y].char,
                    self.colors.get_color(self.main_menu_tiles[x][y].color)
                )
        
        window.border()
        options_subwindow.erase()
        options_subwindow.border()
        
        # Clamp cursor index.
        if cursor_index < 0:
            cursor_index = 0
        elif cursor_index > len(menu_options) - 1:
            cursor_index = len(menu_options) - 1
        
        # Adjust positions relative to screen.
        option_y_pos: int = OPTIONS_SUBWIN_START_Y + 2
        
        # Display menu option choices with cursor.
        start_options_x: int = self.game_height // 2 + self.game_height // 4
        for index, option in enumerate(menu_options):
            window.addstr(
                start_options_x + index + 1,
                option_y_pos, option.text)
            if index == cursor_index:
                window.addstr(
                    start_options_x + index + 1,
                    option_y_pos, option.text, curses.A_REVERSE
                )
        
        # Display the game title.
        TITLE_X_POS: int = start_options_x - 8
        for line in self.title_lines:
            window.addstr(TITLE_X_POS, 3, line)
            TITLE_X_POS += 1
        
        # Place author text (yours truly) wherever it looks nice relative to
        # the position of the title.
        WELCOME_SUBMESSAGE: str = "by Vaiterius (WIP)"
        window.addstr(
            TITLE_X_POS - 1,
            (self.title_width // 2) - 1, WELCOME_SUBMESSAGE)
        
        window.refresh()
        options_subwindow.refresh()
        
        return cursor_index


    def display_confirm_box(
        self, action_to_confirm: str, cursor_index: int) -> int:
        """Display a confirmation box after an important action.
        
        e.g. quitting without saving, overwriting a save
        """
        
        # Box dimensions.
        BOX_HEIGHT: int = self.game_height // 5
        BOX_WIDTH: int = self.game_width // 4
        origin_x: int = (self.game_height // 2) - (BOX_HEIGHT // 2)
        origin_y: int = (self.game_width // 2) - (BOX_WIDTH // 2)
        
        window = curses.newwin(BOX_HEIGHT, BOX_WIDTH, origin_x, origin_y)
        
        window.erase()
        
        window.border()
        
        # Clamp cursor index (only yes or no selections).
        cursor_index = max(0, min(1, cursor_index))
        
        # Prompt header.
        header_msg: str = f"{action_to_confirm.capitalize()}?"
        window.addstr(
            1, self._get_message_center_x(header_msg, BOX_WIDTH), header_msg)
        
        # Line down the middle of the box.
        middle_y: int = BOX_WIDTH // 2
        
        button_1_y: int = middle_y // 2
        button_2_y: int = middle_y + (button_1_y)
        button_x: int = BOX_HEIGHT // 2
        
        # Yes or no selection.
        if cursor_index == 0:
            window.addstr(
                button_x, button_1_y - 2, "> YES <", curses.A_REVERSE)
            window.addstr(button_x, button_2_y, "NO")
        else:
            window.addstr(
                button_x, button_2_y - 2, "> NO <", curses.A_REVERSE)
            window.addstr(button_x, button_1_y, "YES")
        
        window.refresh()
        
        return cursor_index
    

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


    def _get_main_menu_map_tiles(self) -> list[list[Tile]]:
        """A cool randomly-generated dungeon background for the main menu"""
        num_rooms: int = random.randint(15, 20)
        floor: Floor = (
            FloorBuilder((self.game_width - 2, self.game_height - 2))
            .place_walls(tile_type=wall_tile_dim)
            .place_rooms(num_rooms,
                         MIN_MAX_ROOM_WIDTH,
                         MIN_MAX_ROOM_HEIGHT,
                         floor_tile_dim)
            .place_tunnels(floor_tile_dim)
        ).build(dungeon=None)
        return floor.tiles


    def _get_title_lines(self, file_location: str, max_width: str) -> list[str]:
        """Get the lines for the cool ASCII art for the title I got online.
        
        https://ascii.today/
        "Rounded" by Nick Miners
        """
        with open(file_location) as title_file:
            lines: list[str] = []
            for line in title_file:
                # Resize line by adding whitespace to fit max width if needed.
                line = line[:max_width]
                while len(line) < max_width:
                    line += " "
                lines.append(line)
            return lines

    
    def _get_title_dimensions(self, lines: list[str]) -> tuple[int, int]:
        """Get the height and width of the title ASCII art"""
        height: int = len(lines)
        width: int = max([len(line) for line in lines])
        return width, height
    
    
    def _get_message_center_x(self, message: str, window_width: int) -> int:
        """
        Get the center x position to place a message or window in the middle of
        its parent window
        """
        return (window_width // 2) - (len(message) // 2)

