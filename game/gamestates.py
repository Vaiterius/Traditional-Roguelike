from __future__ import annotations

from typing import TYPE_CHECKING, Union
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .entities import Entity
    from .engine import Engine
from .actions import *


class AbstractState(ABC):
    
    @abstractmethod
    def on_enter():
        pass
    
    @abstractmethod
    def handle_input():
        pass
    
    @abstractmethod
    def perform():
        pass
    
    @abstractmethod
    def render():
        pass


class State(AbstractState):
    """Base class for gamestate classes"""
    
    def __init__(self, parent: Entity):
        self.parent = parent


    def on_enter(self, engine: Engine) -> None:
        """Code to run upon switching to another state"""
        pass


    def handle_input(self, engine: Engine) -> Union[Action, State]:
        """Retrieve input from player while in this state"""
        pass


    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        """Perform an action or switch to another state from input"""
        turnable: bool = False
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
        elif isinstance(action_or_state, State):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter(engine)
        
        return turnable


    def render(self, engine: Engine) -> None:
        """Display part of the game belonging to the current gamestate"""
        pass
    
    
    def display_main(self, engine: Engine) -> None:
        """Display the map, message_log, and sidebars"""
        engine.terminal_controller.ensure_right_terminal_size()
        engine.terminal_controller.display_map(
            engine.dungeon.current_floor, engine.player)
        engine.terminal_controller.display_message_log(engine.message_log)
        engine.terminal_controller.display_sidebar(engine.dungeon)


class IndexableOptionsState(State):
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.cursor_index = 0


class MainMenuState(IndexableOptionsState):
    """Menu options for when the player first starts up the game"""
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.menu_options: list[tuple[str, Union[Action, State]]] = [
            ("1) New Game", ExploreState(self.parent)),
            ("2) Continue Game", ContinueGameAction(self.parent)),
            ("3) Help", WaitAction(self.parent)),
            ("4) Quit", QuitGameAction(self.parent))
        ]
    
    def handle_input(self, engine: Engine) -> Union[Action, State]:
        action_or_state: Union[Action, State] = None
        while not action_or_state:
            player_input: str = engine.terminal_controller.get_input()
            
            match player_input:
                case "KEY_ENTER" | "\n":  # Select item to use.
                    action_or_state = self.menu_options[self.cursor_index][1]
                case "KEY_UP":  # Move cursor up.
                    self.cursor_index -= 1
                    break
                case "KEY_DOWN":  # Move cursor down.
                    self.cursor_index += 1
                    break
                
                # QUIT.
                case "Q":
                    action_or_state = QuitGameAction(self.parent)
        
        return action_or_state
    
    
    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        """Perform an action or switch to another state from input"""
        turnable: bool = False
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
            
            # Continue game edge case.
            if isinstance(action_or_state, ContinueGameAction):
                engine.gamestate = ExploreState(self.parent)
                if not engine.dungeon.floors:
                    StartNewGameAction(self.parent).perform(engine)

        elif isinstance(action_or_state, State):
            engine.gamestate = action_or_state
            
            # Starting new game.
            if isinstance(action_or_state, ExploreState):
                StartNewGameAction(self.parent).perform(engine)
                return turnable  # Omit on_enter.
            
            action_or_state.on_enter(engine)
        
        return turnable
    

    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_main_menu(
            self.menu_options, self.cursor_index)
        self.cursor_index = new_cursor_pos


class GameOverState(State):
    """Handle game upon player death"""
        
    def handle_input(self, engine: Engine) -> Union[Action, State]:
        action_or_state: Union[Action, State] = None
        while not action_or_state:
            player_input: str = engine.terminal_controller.get_input()
            
            match player_input:
                case "Q":
                    action_or_state = QuitGameAction(self.parent)
        
        return action_or_state

    
    def render(self, engine: Engine) -> None:
        super().display_main(engine)


class ExploreState(State):
    """Handles player movement and interaction when exploring the dungeon"""

    def on_enter(self, engine: Engine) -> None:
        self.render(engine)
        engine.get_valid_action()


    def handle_input(self, engine: Engine) -> Union[Action, State]:
        action_or_state: Union[Action, State] = None
        while not action_or_state:
            player_input: str = engine.terminal_controller.get_input()
            
            match player_input:
                
                # ACTIONS
                case "KEY_UP":  # Move up.
                    action_or_state = BumpAction(self.parent, dx=-1, dy=0)
                case "KEY_DOWN":  # Move down.
                    action_or_state = BumpAction(self.parent, dx=1, dy=0)
                case "KEY_LEFT":  # Move left.
                    action_or_state = BumpAction(self.parent, dx=0, dy=-1)
                case "KEY_RIGHT":  # Move right.
                    action_or_state = BumpAction(self.parent, dx=0, dy=1)
                case '.':  # Do nothing.
                    action_or_state = WaitAction(self.parent)
                case '>':  # Descend a level.
                    action_or_state = DescendStairsAction(self.parent)
                case '<':  # Ascend a level.
                    action_or_state = AscendStairsAction(self.parent)
                case 'Q':  # Quit game.
                    action_or_state = QuitGameAction(self.parent)
                
                # CHANGE STATE.
                case 'I':  # Head to inventory.
                    action_or_state = InventoryMenuState(self.parent)
                case 'M':  # Head back to main menu.
                    action_or_state = MainMenuState(self.parent)
                case _:
                    action_or_state = None
        
        return action_or_state


    def render(self, engine: Engine) -> None:
        super().display_main(engine)


class InventoryMenuState(IndexableOptionsState):
    """Handles selection/dropping/using of items in player inventory"""
    
    def handle_input(self, engine: Engine) -> Union[Action, State]:
        action_or_state: Union[Action, State] = None
        while not action_or_state:
            player_input: str = engine.terminal_controller.get_input()
            
            match player_input:
                
                # ACTIONS.
                case "KEY_UP":  # Move cursor up.
                    self.cursor_index -= 1
                case "KEY_DOWN":  # Move cursor down.
                    self.cursor_index += 1
                case "KEY_ENTER" | "\n":  # Select item to use.
                    action_or_state = ...
                
                # CHANGE STATE.
                case 'I':
                    action_or_state = ExploreState(self.parent)
                case _:
                    action_or_state = None
            
            self.render(engine)
        
        return action_or_state


    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_inventory(
            engine.player.inventory, self.cursor_index)
        self.cursor_index = new_cursor_pos

