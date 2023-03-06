import sys
import curses
from typing import Optional

from .entities import Player
from .actions import *
from .dungeon import Dungeon
from .terminal_control import TerminalController


class Engine:

    def __init__(self,
                 screen: curses.initscr,
                 player: Player,
                 dungeon: Dungeon,
                 terminal_controller: TerminalController
                 ):
        self.screen = screen
        self.player = player
        self.dungeon = dungeon
        self.terminal_controller = terminal_controller


    def run(self):
        # Game initialization.
        self.dungeon.generate_floor()
        self.dungeon.spawn_player()

        # Main game loop.
        while True:
            # Display screen.
            self.display()
            # Handle player input.
            self.handle_input()
            # World's turn.
            self.process()


    def display(self):
        self.terminal_controller.display(
            self.dungeon.current_floor, self.player)


    def handle_input(self):
        player_input = self.terminal_controller.get_input()
        if player_input == "Q":
            sys.exit(1)
        
        action: Optional[Action] = None
        
        if player_input == "KEY_UP":  # Move up.
            action = WalkAction(dx=-1, dy=0)
        elif player_input == "KEY_DOWN":  # Move down.
            action = WalkAction(dx=1, dy=0)
        elif player_input == "KEY_LEFT":  # Move left.
            action = WalkAction(dx=0, dy=-1)
        elif player_input == "KEY_RIGHT":  # Move right.
            action = WalkAction(dx=0, dy=1)
        
        if action:
            action.perform(self, self.player)


    def process(self):
        pass

