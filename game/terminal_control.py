from __future__ import annotations

import curses
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .entities import Player, Entity
from .color import Color
from .actions import ExploreAction
from .pathfinding import distance_from, bresenham_path_to


class Message:
    """Hold message content and other relevant info"""
    
    def __init__(self, message: str):
        self.message = message
        self.count = 1
    
    
    def __str__(self):
        if self.count > 1:
            return f"{self.message} x{self.count}"
        return self.message


class MessageLog:
    """Message logger for game display"""
    GREETING_MESSAGE = "Welcome to <unnamed game>!"
    
    def __init__(self):
        self.messages: deque = deque([Message(self.GREETING_MESSAGE)])
        self.history: deque = deque([Message(self.GREETING_MESSAGE)])
    
    
    def get(self, index: int) -> str:
        return self.messages[index]
    
    
    def size(self) -> int:
        return len(self.messages)


    def add(self, message: str, debug: bool = False) -> None:
        if debug:
            message = "[DEBUG] " + message
        
        new_message = Message(message)    
        
        # Message is the same as the previous.
        if new_message.message == self.messages[0].message:
            self.messages[0].count += 1
            return

        self.messages.appendleft(new_message)
        self.history.appendleft(new_message)
    
    
    def clear(self) -> None:
        self.messages = deque([Message(self.GREETING_MESSAGE)])


class TerminalController:
    """Handle graphical output of data and terminal input from the player"""

    def __init__(self,
                 screen: curses.initscr,
                 floor_dimensions: tuple[int, int]):
        self.screen = screen
        self.floor_width, self.floor_height = floor_dimensions
        self.colors = Color()  # Fetching available character tile colors.

        curses.curs_set(0)  # Hide cursor.
        
        # TODO maybe make a little wrapper around curses for code readability
        # curses = ew
        
        # MAP CONFIG.
        self.floor_view_height: int = self.floor_height
        self.floor_view_width: int = self.floor_width
        self.floor_view_window = curses.newwin(
            self.floor_view_height + 2, self.floor_view_width + 2,
            0, 0
        )
        
        # MESSAGE LOG CONFIG.
        self.message_log = MessageLog()
        self.message_log_height: int = 10
        self.message_log_width: int = self.floor_view_width + 2
        self.message_log_window = curses.newwin(
            self.message_log_height, self.message_log_width,
            self.floor_view_height + 2, 0
        )
        
        # SIDEBAR CONFIG.
        self.sidebar_width: int = 28
        self.sidebar_height: int = self.floor_view_height \
                                   + self.message_log_height + 2
        self.sidebar = curses.newwin(
            self.sidebar_height, self.sidebar_width,
            0, self.floor_view_width + 2
        )
        
        # Entire game window sizes.
        self.game_height = self.floor_view_height + self.message_log_height + 2
        self.game_width = self.floor_view_width + self.sidebar_width + 2
        
        self.screen.refresh()
        self.floor_view_window.refresh()
        self.message_log_window.refresh()
        self.sidebar.refresh()
    

    def display(self, floor: Floor, player: Player):
        """Output the game data onto the screen"""
        self.ensure_right_terminal_size()
        self.floor_view_window.erase()  # .clear() will cause flickering.
        self.message_log_window.erase()
        self.sidebar.erase()

        # Display dungeon tiles.
        self.floor_view_window.border()
        player_info_temp = f"{player.name} - HP: {player.hp}/{player.max_hp}"
        self.floor_view_window.addstr(0, 2, player_info_temp)
        for x in range(self.floor_view_height):
            for y in range(self.floor_view_width):
                self.floor_view_window.addstr(
                    x + 1, y + 1,
                    floor.tiles[x][y].char,
                    self.colors.get_color(floor.tiles[x][y].color))

        # Display objects.
        # TODO

        # Display entities.
        for creature in floor.creatures:
            if not self.in_player_fov(player, creature, floor):  # TODO refactor to player class
                continue
            self.floor_view_window.addstr(
                creature.x + 1,
                creature.y + 1,
                creature.char,
                self.colors.get_color(creature.color))
        
        # Display player.
        self.floor_view_window.addstr(
            player.x + 1,
            player.y + 1,
            player.char,
            self.colors.get_color(player.color))

        # Display message log.
        self.message_log_window.border()
        self.message_log_window.addstr(0, 2, "MESSAGE LOG")
        cursor = 0
        for i in range(self.message_log_height - 2, 0, -1):
            message = str(self.message_log.get(cursor))
            self.message_log_window.addstr(i, 2, message)
            cursor += 1
            if cursor > self.message_log.size() - 1:
                break
        
        # Display sidebar.
        self.sidebar.border()

        self.floor_view_window.refresh()
        self.message_log_window.refresh()
        self.sidebar.refresh()
    

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
    
    
    def in_player_fov(
        self, player: Player, entity: Entity, floor: Floor) -> bool:
        """Return whether player is able to see an item or enemy"""
        # Save resources and compute if within reasonable range.
        TILE_RANGE: int = 10
        if distance_from(entity.x, entity.y, player.x, player.y) <= TILE_RANGE:

            # Line of sight is blocked.
            paths: list[tuple[int, int]] = bresenham_path_to(
                entity.x, entity.y, player.x, player.y)
            blocked: bool = any(
                [not floor.tiles[x][y].walkable for x,y in paths])
            if blocked or not floor.tiles[entity.x][entity.y].explored:
                return False
            return True
        return False

