from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.dungeon import Dungeon
    from .terminal_control import TerminalController
    from .entities import Player
    from .message_log import MessageLog
from .gamestates import *


class Engine:
    """Drives the main logic of the game"""

    def __init__(self,
                 screen: curses.initscr,
                 player: Player,
                 dungeon: Dungeon,
                 message_log: MessageLog,
                 terminal_controller: TerminalController
                 ):
        self.screen = screen
        self.player = player
        self.dungeon = dungeon
        self.message_log = message_log
        self.terminal_controller = terminal_controller
        
        self.gamestate = MainMenuState(self.player)


    def run(self):
        """Starting the game"""
        # Main game loop.
        while True:
            self.display()
            turnable: bool = self.get_valid_action()
            if not turnable:
                continue
            self.process()


    def display(self) -> None:
        """Display the game to the screen"""
        self.gamestate.render(self)


    def get_valid_action(self) -> bool:
        """Handle player input depending on state"""
        action_or_state = self.gamestate.handle_input(self)
        return self.gamestate.perform(self, action_or_state)  # Can be turnable.


    def process(self) -> None:
        """Proccess world's turn from player's input"""
        # Handle enemy turns.
        if isinstance(self.gamestate, ExploreState):
            creatures = self.dungeon.current_floor.creatures
            for creature in creatures:
                if creature.get_component("ai") and not creature.is_dead:
                    creature.take_turn(self)
        
        # Check if player has died.
        if self.player.is_dead:
            self.gamestate = GameOverState(self.player)
            self.message_log.add("Game over!")
            

