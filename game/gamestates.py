from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Entity
from .actions import *


class State:
    
    def __init__(self, parent: Entity):
        self.parent = parent
    
    def on_enter():
        pass
    
    def handle_input():
        pass
    
    def perform():
        pass
    
    def render():
        pass


class MainMenuState(State):
    pass


class ExploreState(State):
    """Handles player movement and interaction when exploring the dungeon"""

    #         case "KEY_UP":  # Move up.
    #             return BumpAction(self.parent, dx=-1, dy=0)
    #         case "KEY_DOWN":  # Move down.
    #             return BumpAction(self.parent, dx=1, dy=0)
    #         case "KEY_LEFT":  # Move left.
    #             return BumpAction(self.parent, dx=0, dy=-1)
    #         case "KEY_RIGHT":  # Move right.
    #             return BumpAction(self.parent, dx=0, dy=1)

    def on_enter(self):
        pass

    def handle_input(self, terminal_controller):
        action_or_state = None
        while not action_or_state:
            player_input = terminal_controller.get_input()
            
            match player_input:
                case "KEY_UP":  # Move up.
                    action_or_state = BumpAction(self.parent, dx=-1, dy=0)
                case "KEY_DOWN":  # Move down.
                    action_or_state = BumpAction(self.parent, dx=1, dy=0)
                case "KEY_LEFT":  # Move left.
                    action_or_state = BumpAction(self.parent, dx=0, dy=-1)
                case "KEY_RIGHT":  # Move right.
                    action_or_state = BumpAction(self.parent, dx=0, dy=1)
                case ".":  # Do nothing.
                    action_or_state = WaitAction(self.parent)
                
                # TODO add staircase actions
                
                case "I":  # Head to inventory.
                    action_or_state = InventoryMenuState(self.parent)
                case _:
                    action_or_state = None
        
        return action_or_state

    def perform(self, engine, action_or_state):
        if isinstance(action_or_state, Action):
            action_or_state.perform(engine)
        elif isinstance(action_or_state, InventoryMenuState):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter()
        
    
    def render(self, engine):
        engine.terminal_controller.display(engine.dungeon.current_floor, engine.player)


# TODO maybe inherit from common menu state
class InventoryMenuState(State):
    
    def on_enter(self):
        # Initialize cursor delta.
        self.cursor_index_pos = 0
    
    def handle_input(self, terminal_controller):
        action_or_state = None
        while not action_or_state:
            player_input = terminal_controller.get_input()
            
            match player_input:
                case "KEY_UP":
                    action_or_state = RaiseCursorAction(self.parent)
                case "KEY_DOWN":
                    action_or_state = LowerCursorAction(self.parent)
                case "I":
                    action_or_state = ExploreState(self.parent)
                case _:
                    action_or_state = None
        
        return action_or_state
    
    def perform(self, engine, action_or_state):
        if isinstance(action_or_state, Action):
            action_or_state.perform(engine)
        elif isinstance(action_or_state, ExploreState):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter()
            
            # Don't process enemy turns when exiting out of inventory.
            engine.gamestate.render(engine)
            engine.get_valid_action()
    
    def render(self, engine):
        engine.terminal_controller.display_inventory(self.cursor_index_pos)

