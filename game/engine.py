from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.dungeon import Dungeon
    from .terminal_control import TerminalController
    from .entities import Player
from .gamestates import *


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
        
        # Start off exploring for now.
        # TODO change to MainMenuState
        self.gamestate = ExploreState(self.player)


    def run(self):
        """Starting the game"""
        # Game initialization.
        self.dungeon.generate()
        self.dungeon.spawn_player()
        self.dungeon.current_floor.first_room.explore(self)

        # Main game loop.
        while True:
            self.display()
            self.get_valid_action()
            self.process()


    def display(self) -> None:
        """Display the game to the screen"""
        # self.terminal_controller.display(
        #     self.dungeon.current_floor, self.player)
        self.gamestate.render(self)


    def get_valid_action(self) -> None:
        """Handle player input depending on state"""
        action_or_state = self.gamestate.handle_input(self.terminal_controller)
        self.gamestate.perform(self, action_or_state)


    def process(self) -> None:
        """Proccess world's turn from player's input"""
        # Handle enemy turns.
        if isinstance(self.gamestate, ExploreState):
            entities = self.dungeon.current_floor.entities
            for entity in entities:
                if entity.get_component("ai") and not entity.is_dead:
                    # TODO maybe change to take_turn()
                    entity.ai.perform(self)
        # Move cursor for item selection.
        # elif isinstance(self.gamestate, InventoryMenuState):
            

