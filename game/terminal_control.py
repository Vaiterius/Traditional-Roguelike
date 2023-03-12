from __future__ import annotations

import curses
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .entities import Player
from .color import Color


class MessageLog:
    GREETING_MESSAGE = "Welcome to <unnamed game>!"
    
    def __init__(self):
        self.messages: deque = deque([self.GREETING_MESSAGE])
        self.history: deque = deque([self.GREETING_MESSAGE])
    
    
    def get(self, index: int) -> str:
        return self.messages[index]
    
    
    def size(self) -> int:
        return len(self.messages)


    def add(self, message: str, debug: bool = False) -> None:
        if debug:
            message = "[DEBUG] " + message
        self.messages.appendleft(message)
        self.history.appendleft(message)
    
    
    def clear(self) -> None:
        self.messages = deque([self.GREETING_MESSAGE])


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
        
        curses.doupdate()
    

    def display(self, floor: Floor, player: Player):
        """Output the game data onto the screen"""
        self.ensure_right_terminal_size()
        self.floor_view_window.erase()  # .clear() will cause flickering.
        self.message_log_window.erase()
        self.sidebar.erase()

        # Display dungeon tiles.
        self.floor_view_window.box()
        self.floor_view_window.addstr(0, 2, player.name)
        for x in range(self.floor_view_height):
            for y in range(self.floor_view_width):
                self.floor_view_window.addstr(
                    x + 1, y + 1,floor.tiles[x][y].char)

        # Display objects.
        # TODO

        # Display entities.
        for entity in floor.entities:
            self.floor_view_window.addstr(
                entity.x + 1,
                entity.y + 1,
                entity.char,
                self.colors.get_color(entity.color))
        
        # Display player.
        self.floor_view_window.addstr(
            player.x + 1,
            player.y + 1,
            player.char,
            self.colors.get_color(player.color))

        # Display message log.
        self.message_log_window.box()
        self.message_log_window.addstr(0, 2, "MESSAGE LOG")
        cursor = 0
        for i in range(self.message_log_height - 2, 0, -1):
            self.message_log_window.addstr(i, 2, self.message_log.get(cursor))
            cursor += 1
            if cursor > self.message_log.size() - 1:
                break
        
        # Display sidebar.
        self.sidebar.box()

        self.floor_view_window.refresh()
        self.message_log_window.refresh()
        self.sidebar.refresh()
        curses.doupdate()
    

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

