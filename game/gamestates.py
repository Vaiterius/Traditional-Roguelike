from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from pathlib import Path
    from .entities import Entity
    from .engine import Engine
from .actions import *
from .save_handling import (
    get_new_game, fetch_saves, create_new_save, delete_save,
    # overwrite_save
)

# In order, if applicable: arrow keys, numpad keys, and vi keys.
MOVE_KEYS = {
    # Upper-left.
    "KEY_HOME":   (-1, -1),
    "KEY_A1":     (-1, -1),
    'y':          (-1, -1),
    # Up.
    "KEY_UP":     (-1, 0),
    'k':          (-1, 0),
    # Upper-right.
    "KEY_PPAGE":  (-1, 1),
    "KEY_A3":     (-1, 1),
    'u':          (-1, 1),
    # Left.
    "KEY_LEFT":   (0, -1),
    'h':          (0, -1),
    # Right.
    "KEY_RIGHT":  (0, 1),
    'l':          (0, 1),
    # Lower-left.
    "KEY_END":    (1, -1),
    "KEY_C1":     (1, -1),
    # Down.
    "KEY_DOWN":   (1, 0),
    'j':          (1, 0),
    # Lower-right.
    "KEY_NPAGE":  (1, 1),
    "KEY_C3":     (1, 1),
    'n':          (1, 1),
}

WAIT_KEYS = {'.', "KEY_DC", "KEY_B2",}

EXIT_KEYS = {"Q",}
BACK_KEYS = {"KEY_BACKSPACE",}

CONFIRM_KEYS = {"KEY_ENTER", '\n',}


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


    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
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
        engine.terminal_controller.display_sidebar(
            engine.dungeon, engine.player)


class IndexableOptionsState(State):
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.cursor_index = 0


class MainMenuState(IndexableOptionsState):
    """Menu options for when the player first starts up the game"""
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.menu_options: list[tuple[str, Union[Action, State]]] = [
            ("1) New Game", StartNewFromSavesState(self.parent)),
            ("2) Continue Game", ContinueFromSavesState(self.parent)),
            ("3) Help", DoNothingAction(self.parent)),
            ("4) Quit", QuitGameAction(self.parent))
        ]
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in CONFIRM_KEYS:  # Select item to use.
            action_or_state = self.menu_options[self.cursor_index][1]
            
        elif player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index += 1
                action_or_state = DoNothingAction(self.parent)

        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state
    
    
    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_main_menu(
            self.menu_options, self.cursor_index)
        self.cursor_index = new_cursor_pos


class SavesMenuState(IndexableOptionsState):
    
    TITLE = "<None>"
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.saves_dir = Path("saves")
        self.saves: list[Save] = fetch_saves(self.saves_dir)
    
    
    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_saves(
            self.saves, self.cursor_index, self.TITLE)
        self.cursor_index = new_cursor_pos
    
    
class ContinueFromSavesState(SavesMenuState):
    
    TITLE = "CONTINUE A GAME"
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:

        action_or_state: Optional[Union[Action, State]] = None
        if player_input in CONFIRM_KEYS:
            save: Save = self.saves[self.cursor_index]
            if save.is_empty:
                action_or_state = DoNothingAction(self.parent)
            else:
                action_or_state = ContinueGameAction(save)
        
        elif player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index += 1
                action_or_state = DoNothingAction(self.parent)
        
        # Go back to main menu.
        elif player_input in BACK_KEYS:
            action_or_state = MainMenuState(self.parent)
        
        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state
    
    
    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        """Perform an action or switch to another state from input"""
        turnable: bool = False
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
            
            # Play from savefile or from newly-created savefile if empty slot.
            if isinstance(action_or_state, ContinueGameAction):
                create_new_save(engine, self.saves_dir, self.cursor_index)
                engine.gamestate = ExploreState(engine.player)
            
        elif isinstance(action_or_state, State):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter(engine)
        
        return turnable
    

class StartNewFromSavesState(SavesMenuState):
    
    TITLE = "START A NEW GAME"
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in CONFIRM_KEYS:
            # Create save into any slot.
            # save: Save = self.saves[self.cursor_index]
            action_or_state = StartNewGameAction(
                get_new_game(self.cursor_index))
            # # Delete and replace occupied save.
            # else:
            #     path: Path = self.saves_dir / save.path.name
            #     if path.exists():
            #         path.unlink()
            #         action_or_state = StartNewGameAction(
            #             get_new_game(self.cursor_index))
                
        
        elif player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index -= 1
                action_or_state = DoNothingAction(self.parent)
            if x == 1 and y == 0:  # Move cursor down.
                self.cursor_index += 1
                action_or_state = DoNothingAction(self.parent)
        
        # Go back to main menu.
        elif player_input in BACK_KEYS:
            action_or_state = MainMenuState(self.parent)
        
        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state
    
    
    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        """Perform an action or switch to another state from input"""
        turnable: bool = False
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
            
            # Create savefile and play it, replacing any occupied save.
            if isinstance(action_or_state, StartNewGameAction):
                # save: Save = self.saves[self.cursor_index]
                # if save.is_empty:
                #     create_new_save(self.saves_dir, self.cursor_index)
                # else:
                #     overwrite_save(self.saves_dir, self.cursor_index)
                create_new_save(engine, self.saves_dir, self.cursor_index)
                engine.gamestate = ExploreState(engine.player)
            
        elif isinstance(action_or_state, State):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter(engine)
        
        return turnable


# TODO delete current save
class GameOverState(State):
    """Handle game upon player death"""
    
    def __init__(self, parent: Entity, engine: Engine):
        super().__init__(parent)
        delete_save(engine.save)
        
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        action_or_state: Optional[Union[Action, State]] = None
            
        if player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state

    
    def render(self, engine: Engine) -> None:
        super().display_main(engine)


class ExploreState(State):
    """Handles player movement and interaction when exploring the dungeon"""

    def on_enter(self, engine: Engine) -> None:
        self.render(engine)
        engine.get_valid_action()


    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:

        action_or_state: Optional[Union[Action, State]] = None
        # Do an action.
        if player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            action_or_state = BumpAction(self.parent, dx=x, dy=y)
        elif player_input in WAIT_KEYS:
            action_or_state = DoNothingAction(self.parent)
        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        elif player_input == '>':
            action_or_state = DescendStairsAction(self.parent)
        elif player_input == '<':
            action_or_state = AscendStairsAction(self.parent)
        
        # Change state.
        elif player_input == 'i':
            return InventoryMenuState(self.parent)
        elif player_input == 'm':
            return MainMenuState(self.parent)
        
        return action_or_state


    def render(self, engine: Engine) -> None:
        super().display_main(engine)


class InventoryMenuState(IndexableOptionsState):
    """Handles selection/dropping/using of items in player inventory"""
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index += 1
                action_or_state = DoNothingAction(self.parent)
        
        elif player_input in CONFIRM_KEYS:
            action_or_state = DoNothingAction(self.parent)  # TODO
        
        # Change state.
        elif player_input == 'i':
            action_or_state = ExploreState(self.parent)
        
        return action_or_state


    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_inventory(
            engine.player.inventory, self.cursor_index)
        self.cursor_index = new_cursor_pos

