from __future__ import annotations

import sys
import curses
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .actions import Action
    from .dungeon.dungeon import Dungeon
    from .terminal_control import TerminalController
    from .entities import Player
from .actions import BumpAction, WaitAction


class Engine:
    """The main driving logic of the roguelike"""

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
        """Starting the game"""
        # Game initialization.
        self.dungeon.generate_floor()
        self.dungeon.spawn_player()

        # Main game loop.
        while True:
            self.display()
            self.handle_input()
            self.process()


    def display(self):
        """Display the game to the screen"""
        self.terminal_controller.display(
            self.dungeon.current_floor, self.player)


    def handle_input(self):
        """Handle player input"""
        player_input = self.terminal_controller.get_input()
        if player_input == "Q":
            sys.exit(1)
        
        action: Optional[Action] = None
        
        if player_input == "KEY_UP":  # Move up.
            action = BumpAction(self.player, dx=-1, dy=0)
        elif player_input == "KEY_DOWN":  # Move down.
            action = BumpAction(self.player, dx=1, dy=0)
        elif player_input == "KEY_LEFT":  # Move left.
            action = BumpAction(self.player, dx=0, dy=-1)
        elif player_input == "KEY_RIGHT":  # Move right.
            action = BumpAction(self.player, dx=0, dy=1)
        elif player_input == ".":  # Do nothing.
            action = WaitAction(self.player)
        
        if action:
            action.perform(self)


    def process(self):
        """Proccess world's turn from player's input"""
        # Handle enemy turns.
        entities = self.dungeon.current_floor.entities
        for entity in entities:
            if entity.get_component("ai"):
                entity.ai.perform(self)

