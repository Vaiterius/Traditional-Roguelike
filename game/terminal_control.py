from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.floor import Floor
    from .entities import Player
from .color import Color


class TerminalController:
    """Handle graphical output of data and terminal input from the player"""

    def __init__(self, screen: curses.initscr):
        self.screen = screen
        self.colors = Color()  # Fetching available character tile colors.

        # curses.newwin(self.dungeon.floor_width + 1, self.dungeon.floor_height + 1)
        curses.curs_set(0)  # Hide cursor.
        self.msgs = []

    def add_msg(self, msg: str):
        self.msgs.append(msg)
    

    def display(self, floor: Floor, player: Player):
        """Output the game data onto the screen"""
        self.ensure_right_terminal_size(floor)
        self.screen.erase()  # screen.clear() will cause bad flickering.

        # Display dungeon tiles.
        for x in range(floor.height):
            for y in range(floor.width):
                self.screen.addstr(x, y, floor.tiles[x][y].char)

        # Display objects.
        # TODO

        # Display entities.
        for entity in floor.entities:
            self.screen.addstr(entity.x,
                               entity.y,
                               entity.char,
                               self.colors.get_color(entity.color))
        
        # Display player.
        self.screen.addstr(player.x,
                           player.y,
                           player.char,
                           self.colors.get_color(player.color)
                           )

        msg = "" if not self.msgs else self.msgs.pop()
        self.screen.addstr(
            floor.height, 0, msg
        )

        self.screen.refresh()
    

    def ensure_right_terminal_size(self, floor: Floor):
        """Ensure terminal has space for game output"""
        x, y = self.screen.getmaxyx()
        message = "TERMINAL TOO SMALL"
        message_ypos = y // 2 - (len(message) // 2)
        
        # Complain if user resizes terminal too small.
        while x <= floor.height or y <= floor.width:
            self.screen.erase()
            self.screen.addstr(x // 2, message_ypos, message)

            # Update terminal size.
            x, y = self.screen.getmaxyx()
            message_ypos = y // 2 - (len(message) // 2)
            self.screen.refresh()
    

    def get_input(self):
        """Retrieve player input"""
        return self.screen.getkey()

