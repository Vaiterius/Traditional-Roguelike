from __future__ import annotations

import curses
from typing import TYPE_CHECKING, Optional, Union, Any

if TYPE_CHECKING:
    from .dungeon.dungeon import Dungeon
    from .terminal_control import TerminalController
    from .entities import Player
    from .message_log import MessageLog
    from .save_handling import Save
    from .rng import RandomNumberGenerator
from .gamestates import *
from .fov import compute_fov


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
        self.save_meta: Optional[dict[str, Any]] = save.metadata
        self.player: Optional[Player] = save.data.get("dummy")
        self.dungeon: Optional[Dungeon] = None
        self.message_log: Optional[MessageLog] = None
        self.rng: Optional[RandomNumberGenerator] = None
        self.terminal_controller = terminal_controller

        self.gamestate = gamestate
        
        # Displayed and refreshed at runtime.
        self.tiles_in_fov: dict[tuple[int, int], Tile] = {}


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
        # Player's field of view.
        if isinstance(
            self.gamestate,
            (ExploreState, GameEndState, ProjectileTargetState)
        ):
            floor: Floor = self.dungeon.current_floor
            
            def mark_visible(x: int, y: int) -> None:
                if floor.tiles[x][y].char == WALL_TILE:
                    floor.explored_tiles[(x, y)] = wall_tile_dim
                    self.tiles_in_fov[(x, y)] = wall_tile
                elif floor.tiles[x][y].char == FLOOR_TILE:
                    floor.explored_tiles[(x, y)] = floor_tile_dim
                    self.tiles_in_fov[(x, y)] = floor_tile
            
            def is_blocking(x: int, y: int) -> bool:
                return not floor.tiles[x][y].walkable
            
            compute_fov(
                origin=(self.player.x, self.player.y),
                is_blocking=is_blocking,
                mark_visible=mark_visible
            )

        self.gamestate.render(self)
        self.tiles_in_fov = {}  # Refresh.


    def get_valid_action(self) -> bool:
        """Player input will perform an action or change the game state"""
        action_or_state: Optional[Union[Action, State]] = None
        while not action_or_state:
            player_input: Optional[str] = None
            if not self.gamestate.bypassable:  # Skip input or not.
                player_input = self.terminal_controller.get_input()
 
            action_or_state = self.gamestate.handle_input(player_input)

        turnable: bool = self.gamestate.perform(self, action_or_state)
        return turnable


    def process(self) -> None:
        """Proccess world's turn from player's input"""
        # Handle enemy turns.
        if isinstance(self.gamestate, ExploreState):
            if self.player.leveler.can_level_up:
                self.gamestate = LevelUpSelectionState(self.player)
                return

            creatures = self.dungeon.current_floor.creatures
            for creature in creatures:
                if not creature.get_component("ai") or \
                    not creature.get_component("fighter"):
                    continue
                if not creature.fighter.is_dead:
                    creature.take_turn(self)
        
            # Check if player has died.
            if (
                self.player.fighter.is_dead
                and isinstance(self.gamestate, ExploreState)
            ):
                self.gamestate = GameOverEndState(self.player)
                self.message_log.add("Game over!", color="blue")

