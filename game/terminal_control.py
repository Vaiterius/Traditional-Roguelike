import curses

from .dungeon import Floor
from .entities import Player
from .color import Color


class TerminalController:

    def __init__(self, screen: curses.initscr):
        self.screen = screen
        self.colors = Color()

        # curses.newwin(self.dungeon.floor_width + 1, self.dungeon.floor_height + 1)
        curses.curs_set(0)  # Hide cursor.
    

    def display(self, floor: Floor, player: Player):
        self.ensure_right_terminal_size(floor)
        self.screen.erase()  # screen.clear() will cause bad flickering.

        # Display dungeon tiles.
        for x in range(floor.height):
            for y in range(floor.width):
                self.screen.addstr(x, y, floor.tiles[x][y].char)
        
        # Display player.
        self.screen.addstr(player.x,
                           player.y,
                           player.char,
                           self.colors.get_color(player.color)
                           )

        # Display objects.
        # Display entities.

        self.screen.refresh()
    

    def ensure_right_terminal_size(self, floor: Floor):
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
        return self.screen.getkey()

