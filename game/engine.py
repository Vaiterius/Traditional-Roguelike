from __future__ import annotations

import traceback
import curses
from typing import TYPE_CHECKING, Optional, Union, Any

if TYPE_CHECKING:
    from .dungeon.dungeon import Dungeon
    from .terminal_control import TerminalController
    from .entities import Player
    from .message_log import MessageLog
    from .save_handling import Save
from .gamestates import *


class Engine:
    """Drives the main logic of the game"""

    def __init__(self,
                 screen: curses.initscr,
                 save: Save,
                 terminal_controller: TerminalController,
                 gamestate: State
                 ):
        self.screen = screen
        self.save = save
        self.save_meta: Optional[dict[str, Any]] = {}
        self.player: Optional[Player] = save.data.get("dummy")
        self.dungeon: Optional[Dungeon] = None
        self.message_log: Optional[MessageLog] = None
        self.terminal_controller = terminal_controller
        
        self.gamestate = gamestate


    def run(self):
        """Starting the game"""
        # Main game loop.
        # TODO exception handling for errors
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
        """Player input will perform an action or change the game state"""
        action_or_state: Optional[Union[Action, State]] = None
        while not action_or_state:
            player_input: Optional[str] = None
            if not self.gamestate.bypassable:  # Skip input or not.
                player_input = self.terminal_controller.get_input()
 
            action_or_state = self.gamestate.handle_input(player_input)

        # DEBUG
        if self.message_log:
            self.message_log.add(f"action_or_state: {action_or_state.__class__.__name__}", True)
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
        if (
            self.player.is_dead
            and isinstance(self.gamestate, ExploreState)
        ):
            self.gamestate = GameOverState(self.player, self)
            self.message_log.add("Game over!", color="blue")

