from __future__ import annotations

import curses
import itertools
from math import ceil
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from datetime import datetime
    from .dungeon.floor import Floor
    from .dungeon.dungeon import Dungeon
    from .entities import Entity
    from .components.inventory import Inventory
    from .components.leveler import Leveler
    from .components.fighter import Fighter
    from .message_log import Message, MessageLog
    from .gamestates import MenuOption, GameConfig
    from .save_handling import Save
    from .engine import Engine
from .modes import GameStatus
from .dungeon.floor import FloorBuilder
from .tile import *
from .data.config import *
from .entities import Creature, Player, Item, Weapon, Armor
from .components.fighter import StatModifier
from .color import Color
from .render_order import RenderOrder
from .data.config import PROGRESS_BAR_FILLED, PROGRESS_BAR_UNFILLED
from .save_handling import fetch_save
from .rng import RandomNumberGenerator
from .tile import FLOOR_TILE
from .pathfinding import bresenham_path_to


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


def get_message_center_x(message: str, window_width: int) -> int:
    """
    Get the center x position to place a message or window in the middle of
    its parent window
    """
    return (window_width // 2) - (len(message) // 2)


class Box:
    """Textbox wrapper for curses windows"""

    def __init__(self,
                 height: int,
                 width: int,
                 origin_x: int,
                 origin_y: int):
        self.HEIGHT = height
        self.WIDTH = width
        self.origin_x = origin_x
        self.origin_y = origin_y
        
        self._window = curses.newwin(
            self.HEIGHT, self.WIDTH,
            origin_x, origin_y
        )

        self._text = ""
    
    @property
    def window(self) -> curses.newwin:
        return self._window

    def add_header(self,
                   text: str,
                   orientation: str = "center",
                   reversed: bool = False) -> None:
        y: int = 0
        x: int = 0
        if orientation == "left":
            x = 1
        elif orientation == "right":
            x = self.WIDTH - len(text) - 1
        else:
            x = get_message_center_x(text, self.WIDTH)
        
        self.window.addstr(
            y, x, text, (curses.A_REVERSE if reversed else curses.A_NORMAL))
    
    def erase(self) -> None:
        self._window.erase()
    
    def border(self) -> None:
        self._window.border()
    
    def refresh(self) -> None:
        self._window.refresh()
    
    def add_text(self, y: int, x: int, text: str, *args, **kwargs):
        """Write text to the window from y and x positions"""
        self._text = text
        # Offset to not write on border lines.
        y += 1
        x += 1
        self.window.addstr(y, x, text, *args, **kwargs)
    
    def add_wrapped_text(self, y: int, x: int, text: str, *args):
        """Write text to the window within borders and wrap around.
        
        Algorithm inspiration:
        https://colinmorris.github.io/blog/word-wrap-in-pythons-curses-library
        """
        self.window.move(y + 1, x + 1)

        # Each element will be a separate paragraph.
        sentences: list[str] = text.split("\n")


        def words_and_spaces(text: str) -> list[str]:
            """ Get a list of words with empty spaces between elements.
            >>> words_and_spaces('spam eggs ham')
            ['spam', ' ', 'eggs', ' ', 'ham']
            """
            return list(
                itertools.chain.from_iterable(
                    zip(text.split(), itertools.repeat(' '))))[:-1]


        # Fit paragraphs into textbox.
        for text in sentences:
            y, x = self.window.getyx()  # Current coordinates of cursor.
            
            # Whole string fits on current line.
            if len(text) < self.WIDTH - 1:
                self.window.addstr(text, *args)
            # Split on word boundaries and write each word individually.
            else:
                for word in words_and_spaces(text):
                    if len(word) + x <= self.WIDTH - 1:  # Current word fits.
                        self.window.addstr(word, *args)
                    else:  # Go down a line otherwise.
                        if word[0].isspace():
                            word = word[1:]
                        self.window.addstr(y + 1, 1, word, *args)
                    
                    y, x = self.window.getyx()

            self.window.move(y + 2, 1)  # Go down for new paragraph.


class ConfirmBox(Box):
    """Text box but for confirming a boolean option. Cursor bound to y-axis."""

    def __init__(self, height: int, width: int, origin_x: int, origin_y: int):
        super().__init__(height, width, origin_x, origin_y)
        self._index = 0
    
    @property
    def cursor_index(self) -> int:
        return self._index
    
    def position_cursor(self, index: int) -> None:
        """Clamp cursor index"""
        self._index = max(0, min(1, index))
    
    def display_selection(self, option_1: str, option_2: str) -> None:
        """Show whether player selected 'yes' or 'no'"""
        pass


class ConfirmBoxSmall(ConfirmBox):
    """A smaller type of confirm box, typically for one-liner prompts."""

    def display_selection(self, option_1: str, option_2: str) -> None:
        # Line down the middle of the box.
        middle_y: int = self.WIDTH // 2
        
        button_1_y: int = middle_y // 2
        button_2_y: int = middle_y + button_1_y
        buttons_x: int = (self.HEIGHT // 2) - 1

        if self.cursor_index == 0:
            self.add_text(
                buttons_x, button_1_y - 2, f"> {option_1} <", curses.A_REVERSE)
            self.add_text(buttons_x, button_2_y - 2, option_2)
        else:
            self.add_text(
                buttons_x, button_2_y - 4, f"> {option_2} <", curses.A_REVERSE)
            self.add_text(buttons_x, button_1_y, option_1)


class ConfirmBoxLarge(ConfirmBox):
    """An expandable type of confirm box, typically for displaying more text"""

    def display_selection(self, option_1: str, option_2: str) -> None:
        # Line down the middle of the box.
        middle_y: int = self.WIDTH // 2
        
        # Adjust button positions based on text.
        button_1_y: int = get_message_center_x(option_1, middle_y) - 2
        button_2_y: int = middle_y + get_message_center_x(
            option_2, middle_y) - 4
        
        # Determine where along box height to put the buttons.
        buttons_x: int = self.HEIGHT - 4

        if self.cursor_index == 0:
            self.add_text(
                buttons_x, button_1_y - 1, f"> {option_1} <", curses.A_REVERSE)
            self.add_text(buttons_x, button_2_y + 1, option_2)
        else:
            self.add_text(
                buttons_x, button_2_y - 1, f"> {option_2} <", curses.A_REVERSE)
            self.add_text(buttons_x, button_1_y + 1, option_1)


class TerminalController:
    """Handle graphical terminal output of data, the game representation on the
     screen, and input from the player.
    
    In curses, the x-axis corresponds to going down the screen starting from
    the top, and the y-axis corresponds to going across the screen, starting
    from the left.

    | ^
    | |  e.g. (1, 2) would be the the point 2 rows down, 3rd column left
    | |
    X |
    | |
    | |
    | |
    v |------------->
      -------Y------>
    """

    def __init__(self,
                 screen: curses.initscr,
                 floor_dimensions: tuple[int, int]):
        self.screen = screen
        self.floor_width, self.floor_height = floor_dimensions
        self.colors = Color()  # Fetch available character tile colors.
        
        # Keep track of visible enemies using their coordinates as keys.
        self.entities_in_fov = {}
        
        curses.curs_set(0)  # Hide cursor.
        
        # MAP CONFIG.
        self.map_height: int = self.floor_height
        self.map_width: int = self.floor_width
        
        
        # MESSAGE LOG CONFIG.
        self.message_log_height: int = 10
        self.message_log_width: int = self.map_width + 2
        
        
        # SIDEBAR CONFIG.
        self.sidebar_width: int = 28
        self.sidebar_height: int = \
            self.map_height + self.message_log_height + 2
        
        
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
                    tiles_in_fov: dict[tuple[int, int], Tile]
                    ) -> curses.newwin:
        """Display the dungeon map along with entities in view.
        
        The data representation coordinates of the map itself is different from
        the display coordinates with curses windows as it has to account for
        the borders.
        """
        # Create the map window itself.
        window = curses.newwin(self.map_height + 2, self.map_width + 2, 0, 0)
        
        window.erase()
        window.border()

        # Display the floor and wall tiles on the map, with the ones brightened
        # as the tiles in the player's FOV.
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
        
        def is_displayable_entity(entity: Entity) -> bool:
            """Filter entities for sidebar display"""
            return isinstance(entity, (Creature, Item)) and (
                not isinstance(entity, Player)
                and entity.render_order != RenderOrder.CORPSE
            )

        # Iterate through the entities list forwards and backwards at the same
        # time. Forwards for keeping render order (creatures on top of items on
        # top of corpses) and backwards for displaying creatures before items
        # on the entities sidebar of the game view.
        for entity_for_render, entity_for_sidebar in zip(
            floor.entities, reversed(floor.entities)
        ):
            # For display on map.
            if (entity_for_render.x, entity_for_render.y) in tiles_in_fov:
                window.addstr(
                    entity_for_render.x + 1,
                    entity_for_render.y + 1,
                    entity_for_render.char,
                    self.colors.get_color(entity_for_render.color)
                )

            # For display on sidebar.
            if (
                (entity_for_sidebar.x, entity_for_sidebar.y) in tiles_in_fov
                and is_displayable_entity(entity_for_sidebar)
            ):
                self.entities_in_fov[
                    (entity_for_sidebar.x, entity_for_sidebar.y)
                ] = entity_for_sidebar
        
        window.refresh()

        return window


    def display_projectile_target(self,
                                  map_window: curses.window,
                                  player: Player,
                                  tiles_in_fov: dict[tuple[int, int], Tile],
                                  cursor_index_x: int, 
                                  cursor_index_y: int) -> tuple[int, int]:
        """
        Display a path to a target cell towards which a projectile will shoot.

        Uses the current map window and just adds the highlighted target cells
        on top of it.
        """
        # Clamp target to within map.
        if cursor_index_x > self.map_height:
            cursor_index_x = self.map_height
        elif cursor_index_x < 1:
            cursor_index_x = 1
        if cursor_index_y > self.map_width:
            cursor_index_y = self.map_width
        elif cursor_index_y < 1:
            cursor_index_y = 1


        def get_tile_info_from_coords(x: int, y: int) -> tuple[str, str]:
            """Returns the name and character of a tile or entity given a
            coordinate.
            
            Subtract 1 from indices to account for left and top window border
            padding.
            """
            targeted_tile: Optional[Tile] = tiles_in_fov.get((x - 1, y - 1))
            if targeted_tile is None:
                return "", ""

            # Temporarily nclude player to be seen in highlight targeting.
            self.entities_in_fov.update({(player.x, player.y): player})
            targeted_entity: Optional[Entity] = self.entities_in_fov.get(
                (x - 1, y - 1))
            del self.entities_in_fov[(player.x, player.y)]
            if targeted_entity is not None:
                return targeted_entity.name, targeted_entity.char
            
            tile_name: str = (
                "Floor Tile"
                if targeted_tile.char == FLOOR_TILE
                else "Wall Tile"
            )
            return tile_name, targeted_tile.char


        target_name, target_char = get_tile_info_from_coords(
            cursor_index_x, cursor_index_y)
        # Targeting valid cells on the map.
        if target_name != "":
            map_window.addstr(
                cursor_index_x, cursor_index_y, target_char, curses.A_REVERSE)
            target_display: str = f">> TARGET: {target_name} <<"
            map_window.addstr(
                self.map_height + 1,
                get_message_center_x(target_display, self.map_width) - 1,
                target_display
            )

            # Highlight path to target cell from player's coordinates.
            paths: list[tuple[int, int]] = bresenham_path_to(
                player.x + 1, player.y + 1, cursor_index_x, cursor_index_y)[1:]
            for x, y in paths:
                _, path_tile_char = get_tile_info_from_coords(x, y)
                map_window.addstr(x, y, path_tile_char, curses.A_REVERSE)
        else:
            target_display: str = f">> TARGET: Out of range <<"
            map_window.addstr(self.map_height + 1, get_message_center_x(
                target_display,
                self.map_width) - 1,
                target_display,
                self.colors.get_color("red")
            )
            map_window.addstr(
                cursor_index_x,
                cursor_index_y,
                "█",
                self.colors.get_color("red")
            )

        map_window.refresh()

        return cursor_index_x, cursor_index_y
    
    
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
        player_header_center_y = get_message_center_x(
            PLAYER_SECTION_HEADER, SIDEBAR_WIDTH)
        player_subwindow.addstr(
            0, player_header_center_y, PLAYER_SECTION_HEADER)
        player_subwindow.addstr(
            1, 1, player.char, self.colors.get_color(player.color))
        player_subwindow.addstr(1, 3, player.og_name)

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


        # STATS SECTION #
        STATS_SECTION_HEADER = "[ STATS ]"
        STATS_START_X = PLAYER_START_X + PLAYER_HEIGHT
        STATS_HEIGHT = 6
        stats_subwindow = window.subwin(
            STATS_HEIGHT,
            SIDEBAR_WIDTH,
            STATS_START_X,
            self.floor_width + 2)
        stats_subwindow.erase()
        stats_subwindow.border()
        attributes_header_center_y = get_message_center_x(
            STATS_SECTION_HEADER, SIDEBAR_WIDTH)
        stats_subwindow.addstr(
            0, attributes_header_center_y, STATS_SECTION_HEADER)
        stats_subwindow.addstr(1, 1, f"POW: {player.fighter.power}")
        stats_subwindow.addstr(
            2, 1, f"AGI: {player.fighter.agility}")
        stats_subwindow.addstr(
            3, 1, f"VIT: {player.fighter.vitality}")
        stats_subwindow.addstr(4, 1, f"SGE: {player.fighter.sage}")
        stats_subwindow.addstr(1, 9, f"LVL: {player.leveler.level}")
        stats_subwindow.addstr(2, 9, f"XP: {player.leveler.experience}")
        stats_subwindow.addstr(
            3, 9, f"XP for next: {player.leveler.experience_left_to_level_up}")
        stats_subwindow.addstr(
            4, 9, f"Total XP: {player.leveler.total_experience}")
        

        # EQUIPPED GEAR SECTION #
        EQUIPPED_SECTION_HEADER: str = "[ EQUIPPED ]"
        EQUIPPED_SECTION_START_X: int = STATS_START_X + STATS_HEIGHT
        EQUIPPED_SECTION_HEIGHT: int = 6
        equipped_subwindow: curses.window = window.subwin(
            EQUIPPED_SECTION_HEIGHT,
            SIDEBAR_WIDTH,
            EQUIPPED_SECTION_START_X,
            self.floor_width + 2
        )
        equipped_subwindow.erase()
        equipped_subwindow.border()
        EQUIPPED_SECTION_CENTER_Y = get_message_center_x(
            EQUIPPED_SECTION_HEADER, SIDEBAR_WIDTH)
        equipped_subwindow.addstr(
            0, EQUIPPED_SECTION_CENTER_Y - 1, EQUIPPED_SECTION_HEADER)
        
        # Display the gear.
        inventory: Inventory = player.inventory
        weapon: Optional[Weapon] = inventory.equipped_weapon
        head_armor: Optional[Armor] = inventory.equipped_head_armor
        torso_armor: Optional[Armor] = inventory.equipped_torso_armor
        leg_armor: Optional[Armor] = inventory.equipped_leg_armor

        # TODO? truncate text if necessary to fit within writing space
        WEAPON_SLOT_NAME: str = (
            "WEAPON: None" if weapon is None
            else f"WEAPON: {weapon.name}"
        )
        HEAD_SLOT_NAME: str = (
            "  HEAD: None" if head_armor is None
            else f"  HEAD: {head_armor.name}"
        )
        TORSO_SLOT_NAME: str = (
            " TORSO: None" if torso_armor is None
            else f" TORSO: {torso_armor.name}"
        )
        LEG_ARMOR_NAME: str = (
            "   LEG: None" if leg_armor is None
            else f"   LEG: {leg_armor.name}"
        )

        equipped_subwindow.addstr(1, 1, WEAPON_SLOT_NAME)
        equipped_subwindow.addstr(2, 1, HEAD_SLOT_NAME)
        equipped_subwindow.addstr(3, 1, TORSO_SLOT_NAME)
        equipped_subwindow.addstr(4, 1, LEG_ARMOR_NAME)


        # TODO? add status effects section


        # STANDING ON SECTION #
        STANDING_ON_SECTION_HEADER = "[ STANDING ON ]"
        STANDING_ON_START_X = \
            EQUIPPED_SECTION_START_X + EQUIPPED_SECTION_HEIGHT
        STANDING_ON_HEIGHT = 4
        standing_on_subwindow = window.subwin(
            STANDING_ON_HEIGHT,
            SIDEBAR_WIDTH,
            STANDING_ON_START_X,
            self.floor_width + 2)
        standing_on_subwindow.erase()
        standing_on_subwindow.border()
        standing_on_header_center_y = get_message_center_x(
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
        # Can only show 1 entity at a time.
        entity_iter: int = 1
        displayable_entities: list[Entity] = entities[:1]
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
                2, 1, f"   and {remaining_entities} more...")


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
        entities_header_center_y: int = get_message_center_x(
            ENTITIES_SECTION_HEADER, SIDEBAR_WIDTH)
        entities_subwindow.addstr(
            0, entities_header_center_y, ENTITIES_SECTION_HEADER)

        # Display surrounding entities and their health bars.
        max_entities_for_display: int = 4
        displayable_entities_in_fov: dict[tuple[int, int], Creature] = \
            dict(
                itertools.islice(
                    self.entities_in_fov.items(), max_entities_for_display))
        # Show a certain number of entities at a time.
        entity_iter: int = 1
        for _, entity in displayable_entities_in_fov.items():
            # Display enemy name and level if they are a creature.
            entity_title: str = f"{entity.char} {entity.name}"
            if entity.get_component("leveler"):
                entity_title += f" Lvl. {entity.leveler.level}"
            entities_subwindow.addstr(
                entity_iter, 1, entity_title, self.colors.get_color(
                    entity.color))
            
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

                entity_iter += 2  # One more row offset for healthbar.
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
        self.entities_in_fov = {}


        window.refresh()
        player_subwindow.refresh()
        stats_subwindow.refresh()
        equipped_subwindow.refresh()
        standing_on_subwindow.refresh()
        entities_subwindow.refresh()


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
            cursor_index = inventory.max_slots - 1
        elif cursor_index > inventory.max_slots - 1:
            cursor_index = 0

        # List out inventory items.
        for index in range(inventory.max_slots):
            item: Optional[Item] = inventory.get_item(index)
            
            # Shift from 0-9 numbering to 1-10.
            slot_char = chr(97 + index)
            index += 1
            
            # Highlight the currently selected index item.
            optional_highlight = curses.A_NORMAL
            if index == cursor_index + 1:
                optional_highlight = curses.A_REVERSE
            
            slot_value: str = ""
            if item:
                slot_value += (
                    f"{'[E] ' if inventory.is_equipped(item) else ''}"
                    f"{item.name}"
                )
            else:
                slot_value += f"<Empty>"
            
            selection_window.addstr(
                index + 1, 2, slot_value, optional_highlight)
        
        # Display currently-selected item's info.
        selected_item: Optional[Item] = inventory.get_item(cursor_index)
        if selected_item is None:
            item_info_window.addstr(1, 1, "")
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
    

    def display_stats(self) -> int:
        """
        Display more details on player's current combat stats and other
        relevant info for this save.
        """
        pass
    

    def display_levelup_selection(self, 
                                  leveler: Leveler, 
                                  fighter: Fighter, 
                                  cursor_index_x: int,
                                  cursor_index_y: int) -> tuple[int, int]:
        """Choose which attribute to level up.
        
        Upon character levelup, the player has the choice between increasing
        their power, agility, vitality, or sage attributes. Will also have
        an info panel to show new changes.
        """
        # Attribute selection and stats info windows.
        ATTRIBUTE_SELECTION_HEIGHT: int = 9
        ATTRIBUTE_SELECTION_WIDTH: int = self.game_width // 3
        STATS_INFO_HEIGHT: int = 6
        STATS_INFO_WIDTH: int = ATTRIBUTE_SELECTION_WIDTH

        # Topleft corners for windows.
        attribute_selection_origin_x: int = self.game_height // 3
        attribute_selection_origin_y: int = (self.game_width // 2) - \
            (ATTRIBUTE_SELECTION_WIDTH // 2)
        stats_info_origin_x: int = attribute_selection_origin_x + \
            ATTRIBUTE_SELECTION_HEIGHT
        stats_info_origin_y: int = attribute_selection_origin_y

        # Create the windows.
        attribute_selection_window = curses.newwin(
            ATTRIBUTE_SELECTION_HEIGHT, ATTRIBUTE_SELECTION_WIDTH,
            attribute_selection_origin_x, attribute_selection_origin_y
        )
        stats_info_window = curses.newwin(
            STATS_INFO_HEIGHT, STATS_INFO_WIDTH,
            stats_info_origin_x, stats_info_origin_y
        )

        HEADER_TEXT = "LEVEL UP!"

        attribute_selection_window.erase()
        attribute_selection_window.border()
        stats_info_window.erase()
        stats_info_window.border()
        attribute_selection_window.addstr(0, 2, HEADER_TEXT, curses.A_REVERSE)

        # Validate cursor position in 2D.
        if cursor_index_x < 0:
            cursor_index_x = 0
        elif cursor_index_x > 1:
            cursor_index_x = 1

        if cursor_index_y < 0:
            cursor_index_y = 0
        elif cursor_index_y > 1:
            cursor_index_y = 1
        
        # Fill attribute selection window.
        subheader_1 = f"Level {leveler.level} -> {leveler.level + 1}"
        subheader_2 = "Choose an attribute to increase:"
        attribute_selection_window.addstr(1, 2, subheader_1)
        attribute_selection_window.addstr(2, 2, subheader_2)


        @dataclass
        class AttributeInfo:
            display_name: str
            x: int
            y: int
            new_stats: list[str]
        
        
        def get_percent(decimal: float) -> int:
            return round(decimal * 100)

        
        # Variables to prevent strings from getting too long.
        # Power stats.
        melee_damage: int = fighter.damage
        melee_damage_add: int = StatModifier.DAMAGE_PER_POINT
        knockout_chance: int = get_percent(fighter.knockout_chance)
        knockout_chance_add: int = get_percent(
            StatModifier.KNOCKOUT_CHANCE_PER_POINT)
        critical_damage: int = get_percent(fighter.critical_hit_damage_bonus)
        critical_damage_add: int = get_percent(
            StatModifier.CRITICAL_HIT_DAMAGE_BONUS_PER_POINT)
        # Vitality stats.
        max_health: int = fighter.max_health
        max_health_add: int = (
            StatModifier.JUICE_PER_3_POINTS
            if (fighter.vitality - 1) % 3 == 0
            else StatModifier.JUICE_PER_POINT
        )
        # Agility stats.
        hit_chance: int = get_percent(fighter.hit_chance)
        hit_chance_add: int = get_percent(StatModifier.HIT_CHANCE_PER_POINT)
        critical_hit_chance: int = get_percent(fighter.critical_hit_chance)
        critical_hit_chance_add: int = get_percent(
            StatModifier.CRITICAL_HIT_CHANCE_PER_POINT)
        double_hit_chance: int = get_percent(fighter.double_hit_chance)
        double_hit_chance_add: int = get_percent(
            StatModifier.DOUBLE_HIT_CHANCE_PER_POINT)
        # Sage stats.
        max_magicka: int = fighter.max_magicka
        max_magicka_add: int = (
            StatModifier.JUICE_PER_3_POINTS
            if (fighter.sage - 1) % 3 == 0
            else StatModifier.JUICE_PER_POINT
        )

        # Selection of attribute based on cursor index position.
        # Connects to LevelUpSelectionState attributes dictionary.
        ATTRIBUTE_INDICES: dict[tuple[int, int], AttributeInfo] = {
            (0, 0): AttributeInfo(
                display_name=" POWER ",
                x=4, y=5,
                new_stats=[
                    f"DMG (melee): {melee_damage} dmg "
                        f"(+{melee_damage_add})",
                    f"DMG (bow): WIP",
                    f"% to knock out: {knockout_chance}% "
                        f"(+{knockout_chance_add}%)",
                    f"Critcal hit DMG: +{critical_damage}% dmg "
                        f"(+{critical_damage_add}%)"
                ]
            ),
            (0, 1): AttributeInfo(
                display_name=" VITALITY ",
                x=4, y=((ATTRIBUTE_SELECTION_WIDTH // 2) + 2),
                new_stats=[
                    f"Max HP: {max_health} pts (+{max_health_add})",
                    f"HP regen per 10 turns: WIP",
                    f"HP potion yield: WIP",
                    "Debuffs have shorter durations..."
                ]
            ),
            (1, 0): AttributeInfo(
                display_name=" AGILITY ",
                x=6, y=4,
                new_stats=[
                    f"% to hit (melee): {hit_chance}% (+{hit_chance_add}%)",
                    f"% to hit (bow): WIP",
                    f"% to land critical: {critical_hit_chance}% "
                        f"(+{critical_hit_chance_add}%)",
                    f"% to double hit: {double_hit_chance}% "
                        f"(+{double_hit_chance_add}%)"
                ]
            ),
            (1, 1): AttributeInfo(
                display_name=" SAGE ",
                x=6, y=((ATTRIBUTE_SELECTION_WIDTH // 2) + 4),
                new_stats=[
                    f"Max MP: {max_magicka} pts (+{max_magicka_add})",
                    f"MP regen per 10 turns: WIP",
                    f"MP potion yield: WIP",
                    "Various spells are stronger..."
                ]
            )
        }

        selected_attribute: AttributeInfo = ATTRIBUTE_INDICES[
            (cursor_index_x, cursor_index_y)
        ]

        # Highlight the currently selected attribute.
        for _, attribute in ATTRIBUTE_INDICES.items():
            if attribute == selected_attribute:
                attribute_selection_window.addstr(
                    selected_attribute.x,
                    selected_attribute.y,
                    selected_attribute.display_name,
                    curses.A_REVERSE,
                )
            else:
                attribute_selection_window.addstr(
                    attribute.x,
                    attribute.y,
                    attribute.display_name,
                    self.colors.get_color("gold")
                )


        # TODO make numeric stat modifiers green characters.
        # Display attribute info on the bottom.
        for i in range(len(selected_attribute.new_stats)):
            stats_info_window.addstr(i + 1, 2, selected_attribute.new_stats[i])

        attribute_selection_window.refresh()
        stats_info_window.refresh()

        return cursor_index_x, cursor_index_y
    
    
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
            cursor_index = len(saves) - 1
        elif cursor_index > len(saves) - 1:
            cursor_index = 0
        
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
                line_pos, 3, f"({index + 1}) {save.path.name}", highlight_attr)
            
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


        def readable(datetime: datetime) -> datetime:
            """Make datetime formats more human readable"""
            return datetime.strftime('%m/%d/%Y %I:%M %p')

        
        # Empty slot.
        if save.is_empty:
            metadata_window.addstr(1, 1, "<Empty>")
        
        # Save metadata enumerated here.
        else:
            save_info: dict[str, str] = {
                "PLAYER: ": str(save.data.get('player').og_name),
                "GAMEMODE: ": str(save.metadata.get("gamemode").name),
                "VERSION: ": str(save.metadata.get('version')),
                "FLOOR: ": str(save.data.get('dungeon').deepest_floor_idx + 1),
                "CREATED AT: ": str(readable(save.metadata.get("created_at"))),
                "LAST PLAYED: ": str(
                    readable(save.metadata.get('last_played'))),
                "SEED: ": str(save.data.get("rng").seed),
                "SLAYED: ": f"{save.metadata.get('slayed'):,} enemies",
                "TURNS: ": f"{save.metadata.get('turns'):,}"
            }

            # Display status of game.
            if save.metadata.get("status") == GameStatus.DEFEAT:
                metadata_window.addstr(
                    1, get_message_center_x(
                        "DEFEAT", PANEL_WIDTH
                        ), "DEFEAT", self.colors.get_color("red"))
            elif save.metadata.get("status") == GameStatus.VICTORY:
                metadata_window.addstr(
                    1, get_message_center_x(
                        "VICTORY", PANEL_WIDTH
                        ), "VICTORY", self.colors.get_color("green"))
            else:
                metadata_window.addstr(
                    1, get_message_center_x(
                        "ONGOING", PANEL_WIDTH
                        ), "ONGOING", self.colors.get_color("gold"))

            info_index = 3
            ALIGN_INDEX = 14
            for label, value in save_info.items():
                metadata_window.addstr(
                    info_index, ALIGN_INDEX - len(label), label, curses.A_BOLD)
                metadata_window.addstr(info_index, ALIGN_INDEX, value)
                info_index += 1
        
        slots_window.refresh()
        metadata_window.refresh()
        
        return cursor_index
    
    
    def display_main_menu(self,
                          save_meta: dict[str, Any],
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
            cursor_index = len(menu_options) - 1
        elif cursor_index > len(menu_options) - 1:
            cursor_index = 0
        
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
        WELCOME_SUBMESSAGE: str = f"by Vaiterius ({save_meta['version']})"
        window.addstr(
            TITLE_X_POS - 1,
            (self.title_width // 2) - 1, WELCOME_SUBMESSAGE)
        
        window.refresh()
        options_subwindow.refresh()
        
        return cursor_index


    def display_game_config(self,
                            config: GameConfig,
                            cursor_index_x: int,
                            cursor_index_y: int) -> int:
        """
        Display interface for entering player's name, gamemode, and (optional)
        seed.
        
        Index map:
        0 - enter name
        1 - enter seed
        2 - toggle gamemode
        3, 0 - cancel; 3, 1 - confirm and start new game
        """
        # Define window size.
        BOX_HEIGHT: int = 15
        BOX_WIDTH: int = 40
        box = Box(
            height=BOX_HEIGHT,
            width=BOX_WIDTH,
            origin_x=(self.game_height // 2) - (BOX_HEIGHT // 2),
            origin_y=(self.game_width // 2) - (BOX_WIDTH // 2)
        )
        box.erase()
        box.border()
        box.add_header("GAME CONFIG", reversed=True)

        # Clamp index positions.
        if cursor_index_x < 0:
            cursor_index_x = 0
        elif cursor_index_x > 3:
            cursor_index_x = 3
        
        if cursor_index_y < 0:
            cursor_index_y = 0
        elif cursor_index_y > 1:
            cursor_index_y = 1

        # Display.
        
        # Box caption.
        box.add_wrapped_text(
            0, 0,
            "Welcome, new hero! Configure your game before jumping in.",
            curses.A_BOLD
        )
        # Name input.
        name_prompt: str = "How would you like to be called?"
        name_input: str = "<ENTER NAME>"
        if len(config.player_name) > 0:
            name_input = f'{"".join(config.player_name)} is my name...'
        box.add_text(
            3, get_message_center_x(name_prompt, box.WIDTH) - 1, name_prompt)
        box.add_text(
            4,
            get_message_center_x(name_input, box.WIDTH) - 1, name_input,
            curses.A_BOLD
        )
        # Seed input.
        seed_prompt: str = "Seed this game? (leave blank if none)"
        seed_input: str = "<ENTER SEED>"
        if len(config.seed) > 0:
            seed_input = "".join(config.seed)
        box.add_text(
            6, get_message_center_x(seed_prompt, box.WIDTH) - 1, seed_prompt)
        box.add_text(
            7,
            get_message_center_x(seed_input, box.WIDTH) - 1,
            seed_input,
            curses.A_BOLD
        )
        # Gamemode toggle.
        gamemode_prompt: str = "Play on endless dungeon mode? (toggle)"
        gamemode_choice: str = (
            'NORMAL' if config.is_normal_gamemode else 'ENDLESS')
        box.add_text(
            9,
            get_message_center_x(gamemode_prompt, box.WIDTH) - 1,
            gamemode_prompt
        )
        box.add_text(10, 10, "Game mode: ", curses.A_BOLD)
        box.add_text(10, 21, gamemode_choice, curses.A_BOLD)
        # Action buttons.
        middle_y: int = box.WIDTH // 2
        cancel_button: str = "CANCEL"
        cancel_button_y: int = middle_y - (len(cancel_button) * 2)
        confirm_button: str = "CONFIRM"
        confirm_button_y: int = middle_y + len(confirm_button) - 3
        box.add_text(12, cancel_button_y, cancel_button)
        box.add_text(12, confirm_button_y, confirm_button)
        
        # Indicate which section the user is currently at. Note that for the
        # name, seed, and gamemode indices, the y index does not matter.
        match (cursor_index_x, cursor_index_y):
            case (0, _):  # Name input.
                box.add_text(
                    4, get_message_center_x(name_input, box.WIDTH) - 1,
                    name_input,
                    curses.A_REVERSE
                )
            case (1, _):  # Seed input.
                box.add_text(
                    7, get_message_center_x(seed_input, box.WIDTH) - 1,
                    seed_input,
                    curses.A_REVERSE
                )
            case (2, _):  # Gamemode toggle.
                box.add_text(10, 21, gamemode_choice, curses.A_REVERSE)
            case (3, 0):  # Go back.
                box.add_text(
                    12, cancel_button_y - 2,
                    f"> {cancel_button} <",
                    curses.A_REVERSE
                )
            case (3, 1):  # Start game.
                box.add_text(
                    12, confirm_button_y - 2,
                    f"> {confirm_button} <",
                    curses.A_REVERSE
                )

        box.refresh()

        return cursor_index_x, cursor_index_y


    # TODO make prettier and add more stats.
    def display_gameover(self, engine: Engine) -> None:
        """Display popup indicating player has died, with stats"""
        # Box dimensions.
        BOX_HEIGHT: int = self.game_height // 5
        BOX_WIDTH: int = self.game_width // 3
        origin_x: int = (self.game_height // 2) - (BOX_HEIGHT // 2)
        origin_y: int = (self.game_width // 2) - (BOX_WIDTH // 2)
        
        window = curses.newwin(BOX_HEIGHT, BOX_WIDTH, origin_x, origin_y)

        window.erase()
        window.border()

        # Information.
        name: str = engine.player.og_name
        current_floor: str = str(engine.dungeon.current_floor_idx + 1)
        deepest_floor: str = str(engine.dungeon.deepest_floor_idx + 1)
        level: str = str(engine.player.leveler.level)

        HEADER: str = "RIP BOZO"

        window.addstr(0, get_message_center_x(
            HEADER, BOX_WIDTH), HEADER, curses.A_REVERSE)
        window.addstr(
            1, 1, f"{name} died on floor {current_floor} at level {level}")
        window.addstr(2, 1, f"Made it up to floor {deepest_floor}")

        window.refresh()


    def display_confirm_box(self,
                            large: bool,
                            header: str,
                            action_text: str,
                            cursor_index: int,
                            option_1: str = "YES",
                            option_2: str = "NO") -> int:
        """Display a confirmation box after an important action.
        
        e.g. quitting without saving, overwriting a save
        """
        # Dimensions.
        height: int = (self.game_height // 5) - 1
        width: int = self.game_width // 4
        num_text_lines: int = len(action_text.split("\n"))

        # Determine what kind of confirm box to use.
        box: Optional[ConfirmBox] = None
        if large:
            height = (self.game_height // 2)
            width = (self.game_width // 3) + 6
            box = ConfirmBoxLarge(
                height=height,
                width=width,
                origin_x=(self.game_height // 2) - (height // 2),
                origin_y=(self.game_width // 2) - (width // 2)
            )
        else:
            box = ConfirmBoxSmall(
                height=height,
                width=width,
                origin_x=(self.game_height // 2) - (height // 2),
                origin_y=(self.game_width // 2) - (width // 2)
            )
            
        box.erase()
        box.border()

        if header:
            box.add_header(header, reversed=True)
        
        if action_text:
            if large:  # Start text left-side.
                box.add_wrapped_text(0, 0, action_text)
            else:  # Place text in the middle.
                action_text = f"{action_text.capitalize()}?"
                box.add_text(
                    0, get_message_center_x(action_text, box.WIDTH) - 1,
                    action_text
                )

        # Update from cursor index.
        box.position_cursor(cursor_index)
        box.display_selection(option_1, option_2)
        
        box.refresh()
        
        return box.cursor_index
    

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
        """A cool, randomly-generated dungeon background for the main menu"""
        rng = RandomNumberGenerator(seed=None)
        num_rooms: int = rng.randint(15, 20)
        floor: Floor = (
            FloorBuilder(rng, (self.game_width - 2, self.game_height - 2))
            .place_walls(tile_type=wall_tile_dim)
            .place_rooms(num_rooms,
                         MIN_MAX_ROOM_WIDTH,
                         MIN_MAX_ROOM_HEIGHT,
                         floor_tile_dim)
            .place_tunnels(floor_tile_dim)
        ).build(dungeon=None)
        return floor.tiles


    def _get_title_lines(
            self, file_location: str, max_width: str) -> list[str]:
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

