from __future__ import annotations

import curses.ascii
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Union, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    import curses
    from pathlib import Path
    from .entities import Entity
    from .engine import Engine
    from .entities import Weapon
from .actions import *
from .components.fighter import Fighter
from .save_handling import Save, get_new_game, fetch_saves

# In order, if applicable: arrow keys, numpad keys, and vi keys. Separated
# so as to not read vi keys when typing characters.

# No support for in-between directions.
ARROW_MOVE_KEYS: dict[str, tuple[int, int]] = {
    # Up.
    "KEY_UP":     (-1, 0),
    # Left.
    "KEY_LEFT":   (0, -1),
    # Right.
    "KEY_RIGHT":  (0, 1),
    # Down.
    "KEY_DOWN":   (1, 0),
}
NON_ARROW_MOVE_KEYS: dict[str, tuple[int, int]] = {
    # Upper-left.
    "KEY_HOME":   (-1, -1),
    "KEY_A1":     (-1, -1),
    'y':          (-1, -1),
    # Up.
    'k':          (-1, 0),
    # Upper-right.
    "KEY_PPAGE":  (-1, 1),
    "KEY_A3":     (-1, 1),
    'u':          (-1, 1),
    # Left.
    'h':          (0, -1),
    # Right.
    'l':          (0, 1),
    # Lower-left.
    "KEY_END":    (1, -1),
    "KEY_C1":     (1, -1),
    "b":          (1, -1),
    # Down.
    'j':          (1, 0),
    # Lower-right.
    "KEY_NPAGE":  (1, 1),
    "KEY_C3":     (1, 1),
    'n':          (1, 1),
}
MOVE_KEYS: dict[str, tuple[int, int]] = {
    **ARROW_MOVE_KEYS, **NON_ARROW_MOVE_KEYS}

WAIT_KEYS: set[str] = {'.', "KEY_DC", "KEY_B2",}
EXIT_KEYS: set[str] = {"Q",}
BACK_KEYS: set[str] = {"KEY_BACKSPACE",}
# We won't add MENU_KEYS to ANY_KEYS to avoid accepting them as valid any-input
# where it's not appropriate.
MENU_KEYS: set[str] = {"m",} 
CONFIRM_KEYS: str[str] = {"KEY_ENTER", '\n',}

# All.
ANY_KEYS: str[str] = set(MOVE_KEYS).union(
    WAIT_KEYS, EXIT_KEYS, BACK_KEYS, CONFIRM_KEYS)


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
        
        # Quick hack because I don't know any other: if enabled, it will bypass
        # the need to get input and execute the next state switch. Useful for
        # confirming a prompt box which will do the next action without getting
        # input again from the user.
        # 
        # Also, this should only be changed on a regular gamestate and NOT
        # during a confirm box state.
        self.bypassable: bool = False


    def on_enter(self, engine: Engine) -> None:
        """Code to run upon switching to another state"""
        pass
    
    
    def on_exit(self, engine: Engine) -> None:
        """Code to run upon exiting the current state"""
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
            engine.gamestate.on_exit(engine)
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
            engine.dungeon.current_floor, engine.tiles_in_fov)
        engine.terminal_controller.display_message_log(engine.message_log)
        engine.terminal_controller.display_sidebar(
            engine.dungeon, engine.player)


class IndexableOptionsState(State):
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.cursor_index_y = 0
        self.cursor_index_x = 0  # 2D selection support.


class Confirmation:
    """Value holder for any state that asks to confirm some action.
    
    Booleans can't be passed by reference so wrap it in something mutable.
    """
    def __init__(self, result: bool = False):
        self.result = result


class ConfirmBoxState(IndexableOptionsState):
    """Have user confirm their intended, significant action"""
    
    def __init__(self,
                 parent,
                 parent_state: State,
                 confirmation: Confirmation,
                 header: str,
                 action_text: str,
                 large: bool = False,
                 option_1: str = "YES",
                 option_2: str = "NO"):
        super().__init__(parent)
        self.parent_state = parent_state
        self.confirmation = confirmation
        self.header = header
        self.action_text = action_text
        self.large = large
        self.option_1 = option_1
        self.option_2 = option_2
    
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in CONFIRM_KEYS:
            if self.cursor_index_y == 0:  # Selected confirm.
                self.confirmation.result = True
            action_or_state = self.parent_state
            
        elif player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == 0 and y == -1:  # Move cursor left.
                self.cursor_index_y -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 0 and y == 1:  # Move cursor right.
                self.cursor_index_y += 1
                action_or_state = DoNothingAction(self.parent)
        
        return action_or_state
    
    
    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_confirm_box(
            self.large,
            self.header,
            self.action_text,
            self.cursor_index_y,
            self.option_1,
            self.option_2
        )
        self.cursor_index_y = new_cursor_pos


@dataclass
class MenuOption:
    """Encapsulates selection action for a main menu option"""
    text: str
    action_or_state: Union[Action, State]


class MainMenuState(IndexableOptionsState):
    """Menu options for when the player first starts up the game"""
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.menu_options: list[MenuOption] = [
            MenuOption(" New Game ", StartNewGameMenuState(self.parent)),
            MenuOption(
                " Continue Game ", ContinueGameMenuState(self.parent)),
            MenuOption(" Help ", DoNothingAction(self.parent)),  # TODO
            MenuOption(" Quit ", QuitGameAction(self.parent))
        ]
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in CONFIRM_KEYS:  # Select item to use.
            action_or_state = \
                self.menu_options[self.cursor_index_y].action_or_state
            
        elif player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index_y -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index_y += 1
                action_or_state = DoNothingAction(self.parent)

        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state
    
    
    def render(self, engine: Engine) -> None:
        new_cursor_pos: int = engine.terminal_controller.display_main_menu(
            engine.save_meta, self.menu_options, self.cursor_index_y)
        self.cursor_index_y = new_cursor_pos


class ListSavesMenuState(IndexableOptionsState):
    
    TITLE = "<None>"
    
    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.saves_dir = Path("saves")
        self.saves: list[Save] = fetch_saves(self.saves_dir)
        
        self.confirm_overwrite: Optional[Confirmation] = None
        self.confirm_delete: Optional[Confirmation] = None
    
    
    def render(self, engine: Engine) -> None:
        # engine.terminal_controller.displ
        new_cursor_pos: int = engine.terminal_controller.display_saves(
            self.saves, self.cursor_index_y, self.TITLE)
        self.cursor_index_y = new_cursor_pos


    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        # Handle shared cursor movement for subclasses.
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index_y -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index_y += 1
                action_or_state = DoNothingAction(self.parent)
        
        return action_or_state
    
    
    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        """Perform an action or switch to another state from input"""
        turnable: bool = False
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
            
            # Go explore after starting a new game or continuing a
            # previously-saved game.
            if (
                isinstance(action_or_state, StartNewGameAction)
                or isinstance(action_or_state, ContinueGameAction)
            ):
                engine.gamestate = ExploreState(engine.player)
            
        elif isinstance(action_or_state, State):
            engine.gamestate = action_or_state
            engine.gamestate.on_enter(engine)
        
        return turnable


@dataclass
class GameConfig:
    """Encapsulates player setup data for starting a new game"""
    player_name: list[str]
    seed: list[str]
    is_normal_gamemode: bool


class EnterGameConfigState(IndexableOptionsState):
    """On new game create, enter in the player's name, gamemode, and (optional)
    seed.
    
    Index map:
    0 - enter name
    1 - enter seed
    2 - toggle gamemode
    3, 0 - cancel; 3, 1 - confirm and start new game
    """
    MAX_CHARACTER_LENGTH: int = 22

    def __init__(self,
                 parent: Entity,
                 prev_state: StartNewGameMenuState):
        super().__init__(parent)
        self.cursor_index_y = 1  # Start right side when scrolling to buttons.
        self._prev_state = prev_state
        self._config: Optional[GameConfig] = GameConfig(
            player_name=[], seed=[], is_normal_gamemode=True)

    def _is_valid_input(self, player_input: str) -> bool:
        """Determine if player input is valid by these allowed characters"""
        return (
            len(player_input) == 1
            and (curses.ascii.isalnum(player_input) or player_input == " ")
        )
    
    def _handle_character_stack(self,
                                characters: list[str],
                                player_input: str) -> None:
        """Handle inputs in modifying either the name or seed stack"""
        if player_input in BACK_KEYS and characters != []:
            characters.pop()
        elif (
            self._is_valid_input(player_input)
            and len(characters) < self.MAX_CHARACTER_LENGTH
        ):
            characters.append(player_input)
    

    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        """
        Handle character inputs for name and seed entries as well as boolean
        switching for gamemode.
        """
        action_or_state: Optional[Union[Action, State]] = None

        # Can go back with a backspace.
        if player_input in BACK_KEYS:
            action_or_state = self._prev_state

        # Moving up and down, and left and right if applicable.
        elif player_input in ARROW_MOVE_KEYS:
            x, y = ARROW_MOVE_KEYS[player_input]
            if x == -1:
                self.cursor_index_x -= 1
            elif x == 1:
                self.cursor_index_x += 1
            if y == -1:
                self.cursor_index_y -= 1
            elif y == 1:
                self.cursor_index_y += 1

        # 0 and 1 for name and seed entry, respectively.
        if self.cursor_index_x in (0, 1):
            if self.cursor_index_x == 0:
                self._handle_character_stack(
                    self._config.player_name, player_input)
            elif self.cursor_index_x == 1:
                self._handle_character_stack(
                    self._config.seed, player_input)

        # 2 for toggling gamemode.
        elif self.cursor_index_x == 2:
            if player_input in CONFIRM_KEYS:
                self._config.is_normal_gamemode = \
                    not self._config.is_normal_gamemode

        # 3 for canceling/confirming.
        elif self.cursor_index_x == 3:
            if self.cursor_index_y == 0:  # Cancel and go back.
                if player_input in CONFIRM_KEYS:
                    action_or_state = self._prev_state
            elif self.cursor_index_y == 1:  # Confirm and start new game.
                if player_input in CONFIRM_KEYS:
                    gamemode: GameMode = GameMode.NORMAL \
                        if self._config.is_normal_gamemode else GameMode.ENDLESS
                    action_or_state = StartNewGameAction(
                        get_new_game(gamemode, self._prev_state.cursor_index_y),
                        self._prev_state.saves_dir,
                        self._prev_state.cursor_index_y,
                        player_name="".join(self._config.player_name),
                        seed="".join(self._config.seed),
                    )
        
        if not action_or_state:
            action_or_state = DoNothingAction(self.parent)
        
        return action_or_state
    

    def render(self, engine: Engine) -> None:
        # Return as (x, y).
        new_cursor_pos: tuple[int, int] = \
            engine.terminal_controller.display_game_config(
            self._config, self.cursor_index_x, self.cursor_index_y
        )
        self.cursor_index_x, self.cursor_index_y = new_cursor_pos
    

    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        turnable: bool = False

        # Do nothing or start new game.
        if isinstance(action_or_state, Action):
            turnable = action_or_state.perform(engine)
            if isinstance(action_or_state, StartNewGameAction):
                engine.gamestate.on_exit(engine)
                engine.gamestate = ExploreState(engine.player)
        # Going back to saves menu.
        elif isinstance(action_or_state, State):
            engine.gamestate.on_exit(engine)
            engine.gamestate = action_or_state
            engine.gamestate.on_enter(engine)
        
        return turnable
    

    def on_enter(self, engine: Engine) -> None:
        """Show cursor when typing"""
        curses.curs_set(1)

    def on_exit(self, engine: Engine) -> None:
        """Unshow cursor"""
        curses.curs_set(0)
    

class StartNewGameMenuState(ListSavesMenuState):
    
    TITLE = "START A NEW GAME"
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        # Inherit cursor movement.
        action_or_state: Optional[Union[Action, State]] = \
            super().handle_input(player_input)
        if action_or_state is not None:
            return action_or_state
        
        # Player has confirmed to overwrite a save.
        if (
            self.confirm_overwrite
            and self.confirm_overwrite.result is True
        ):
            self.confirm_overwrite = None
            # action_or_state = EnterNameState(self.parent, self, [])
            action_or_state = EnterGameConfigState(self.parent, self)
        
        # Player has confirmed to delete a save.
        if self.confirm_delete and self.confirm_delete.result is True:
            self.confirm_delete = None
            return DeleteSaveAction(
                Save.get_empty(), self.saves_dir, self.cursor_index_y)

        self.bypassable = False

        if player_input in CONFIRM_KEYS:
            # Check if selected an occupied slot for overwrite, ask to confirm.
            if not self.saves[self.cursor_index_y].is_empty:
                self.confirm_overwrite = Confirmation()
                action_or_state = ConfirmBoxState(
                    self.parent, self,
                    self.confirm_overwrite, "", "overwrite save")
                self.bypassable = True
            else:
                action_or_state = EnterGameConfigState(self.parent, self)
        
        # Delete a save.
        elif player_input == 'x':
            if not self.saves[self.cursor_index_y].is_empty:
                self.confirm_delete = Confirmation()
                action_or_state = ConfirmBoxState(
                    self.parent, self, self.confirm_delete, "", "delete save")
                self.bypassable = True
        
        # Go back to main menu.
        elif player_input in BACK_KEYS:
            action_or_state = MainMenuState(self.parent)
        
        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state


class ContinueGameMenuState(ListSavesMenuState):
    
    TITLE = "CONTINUE A GAME"
    
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        # Inherit cursor movement.
        action_or_state: Optional[Union[Action, State]] = \
            super().handle_input(player_input)
        if action_or_state is not None:
            return action_or_state
        
        # Player has confirmed to delete a save.
        if self.confirm_delete and self.confirm_delete.result is True:
            self.confirm_delete = None
            return DeleteSaveAction(
                Save.get_empty(), self.saves_dir, self.cursor_index_y)
        
        self.bypassable = False

        if player_input in CONFIRM_KEYS:
            save: Save = self.saves[self.cursor_index_y]
            # Can't continue an empty save.
            if save.is_empty:
                action_or_state = DoNothingAction(self.parent)
            # Can't continue after being defeated.
            elif save.metadata.get("status") == GameStatus.DEFEAT:
                action_or_state = DoNothingAction(self.parent)
            else:
                action_or_state = ContinueGameAction(
                    save, self.saves_dir, self.cursor_index_y)
        
        # Delete a save.
        elif player_input == 'x':
            if not self.saves[self.cursor_index_y].is_empty:
                self.confirm_delete = Confirmation()
                action_or_state = ConfirmBoxState(
                    self.parent, self, self.confirm_delete, "", "delete save")
                self.bypassable = True
        
        # Go back to main menu.
        elif player_input in BACK_KEYS:
            action_or_state = MainMenuState(self.parent)
        
        elif player_input in EXIT_KEYS:
            action_or_state = QuitGameAction(self.parent)
        
        return action_or_state


class GameOverState(State):
    """Delete save if player dies and return to main menu"""
    
    def __init__(self, parent: Entity):
        super().__init__(parent)

        
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        action_or_state: Optional[Union[Action, State]] = None
        
        # TODO maybe accept only enter/exit keys and state that in display.
        if player_input in ANY_KEYS:
            action_or_state = OnPlayerDeathAction(self.parent)
        
        return action_or_state
    
    
    def perform(
        self, engine: Engine, action_or_state: Union[Action, State]) -> bool:
        turnable: bool = super().perform(engine, action_or_state)

        if isinstance(action_or_state, OnPlayerDeathAction):
            engine.gamestate = MainMenuState(self.parent)
        
        return turnable

    
    def render(self, engine: Engine) -> None:
        super().display_main(engine)
        engine.terminal_controller.display_gameover(engine)


class ExploreState(State):
    """Handles player movement and interaction when exploring the dungeon"""

    def __init__(self, parent: Entity):
        super().__init__(parent)
        self.confirm_savequit_to_menu: Optional[Confirmation] = None
        self.confirm_savequit_game: Optional[Confirmation] = None
        self.confirm_mainquest_finish: Optional[Confirmation] = None
    

    def on_enter(self, engine: Engine) -> None:
        self.render(engine)


    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:

        action_or_state: Optional[Union[Action, State]] = None
        
        # Player has confirmed to save and quit to menu.
        if (
            self.confirm_savequit_to_menu
            and self.confirm_savequit_to_menu.result is True
        ):
            self.confirm_savequit_to_menu = None
            return SaveAction(self.parent)
        
        # Player has confirmed to save and quit game.
        if (
            self.confirm_savequit_game
            and self.confirm_savequit_game.result is True
        ):
            self.confirm_savequit_game = None
            return SaveAndQuitAction(self.parent)
        
        # Player has confirmed to exit game after completing main quest.
        if (
            self.confirm_mainquest_finish
            and self.confirm_mainquest_finish.result is True
        ):
            self.confirm_savequit_to_menu = None
            return SaveAction(self.parent)

        self.bypassable = False
        
        # Do an action.
        if player_input in MOVE_KEYS:
            dx, dy = MOVE_KEYS[player_input]
            action_or_state = BumpAction(self.parent, dx=dx, dy=dy)
        elif player_input in WAIT_KEYS:
            action_or_state = DoNothingAction(self.parent)
        elif player_input == '>':
            action_or_state = DescendStairsAction(self.parent)
        elif player_input == '<':
            action_or_state = AscendStairsAction(self.parent)
        
        # Use projectile if applicable weapon is equipped.
        elif player_input in CONFIRM_KEYS:
            weapon: Optional[Weapon] = self.parent.inventory.weapon
            action_or_state = HandleSpecialWeaponAction(self.parent, weapon)

        # Pick up item.
        elif player_input == 'p':
            action_or_state = PickUpItemAction(self.parent)
        
        # Save and return to main menu.
        elif player_input in MENU_KEYS:
            self.confirm_savequit_to_menu = Confirmation()
            action_or_state = ConfirmBoxState(
                self.parent, self, self.confirm_savequit_to_menu, "", "save and go back to menu"
            )
            self.bypassable = True
        
        # Save and quit application.
        elif player_input in EXIT_KEYS:
            self.confirm_savequit_game = Confirmation()
            action_or_state = ConfirmBoxState(
                self.parent, self, self.confirm_savequit_game, "", "save and quit game")
            self.bypassable = True

        elif player_input == '\t' or player_input == 'i':
            return InventoryMenuState(self.parent)
        
        return action_or_state
    
    
    def perform(
        self, engine: Engine, action_or_state: Union[Action, State]) -> bool:
        turnable: bool = super().perform(engine, action_or_state)

        if isinstance(action_or_state, SaveAction):
            engine.gamestate = MainMenuState(self.parent)
        
        return turnable


    def render(self, engine: Engine) -> None:
        super().display_main(engine)


class ProjectileTargetState(State):
    """Handles choosing an target cell to shoot a projectile"""

    def __init__(self, 
                 parent: Entity, 
                 weapon: Weapon, 
                 cursor_index_x: int = 0, 
                 cursor_index_y: int = 0):
        super().__init__(parent)
        self._weapon = weapon
        # Default position if no enemy in sight.
        if cursor_index_x == 0 and cursor_index_y == 0:
            self.cursor_index_x: int = self.parent.x + 1
            self.cursor_index_y: int = self.parent.y + 1
    

    # TODO
    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        action_or_state: Optional[Union[Action, State]] = None
        
        # Out of charges.
        if self._weapon.projectable.uses_left < 1:
            return ExploreState(self.parent)

        # Cancel action.
        if player_input in BACK_KEYS:
            action_or_state = ExploreState(self.parent)

        # TODO Move target.
        if player_input in MOVE_KEYS:
            dx, dy = MOVE_KEYS[player_input]

            self.cursor_index_x += dx
            self.cursor_index_y += dy

            action_or_state = DoNothingAction(self.parent)

        # TODO Attack target.
        if player_input in CONFIRM_KEYS:
            action_or_state = self._weapon.projectable.get_action_or_state(
                self.parent)

        return action_or_state


    def perform(
        self, engine: Engine, action_or_state: Union[Action, State]) -> bool:
        turnable: bool = super().perform(engine, action_or_state)
        return turnable
    
    # TODO
    def render(self, engine: Engine) -> None:
        map_window: curses.window = engine.terminal_controller.display_map(
            engine.dungeon.current_floor, engine.tiles_in_fov)
        new_cursor_pos: tuple[int, int] = \
            engine.terminal_controller.display_projectile_target(
            map_window, engine.player, engine.tiles_in_fov,
            self.cursor_index_x, self.cursor_index_y
        )
        self.cursor_index_x, self.cursor_index_y = new_cursor_pos


class InventoryMenuState(IndexableOptionsState):
    """Handles selection/dropping/using of items in player inventory"""

    def handle_input(
        self, player_input: str) -> Optional[Union[Action, State]]:
        
        action_or_state: Optional[Union[Action, State]] = None
        if player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index_y -= 1
                action_or_state = DoNothingAction(self.parent)
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index_y += 1
                action_or_state = DoNothingAction(self.parent)
        
        # "Activate" item.
        elif player_input in CONFIRM_KEYS:
            item: Optional[Item] = self.parent.inventory.get_item(
                self.cursor_index_y)
            if item is None:
                action_or_state = DoNothingAction(self.parent)
            # Quaff potion.
            elif item.get_component("consumable") is not None:
                action_or_state = item.consumable.get_action_or_state(
                    self.parent)
            # Equip/unequip gear.
            elif item.get_component("equippable") is not None:
                action_or_state = item.equippable.get_action_or_state(
                    self.parent)
        
        # Drop Item.
        elif player_input == 'd':
            item: Optional[Item] = self.parent.inventory.get_item(
                self.cursor_index_y)
            if item:
                action_or_state = DropItemAction(self.parent, item)
        # Switch back from inventory.
        elif player_input == '\t' or player_input == 'i' or \
            player_input in BACK_KEYS:
            action_or_state = ExploreState(self.parent)
        
        return action_or_state

    
    def perform(
        self, engine: Engine, action_or_state: Union[Action, State]) -> bool:
        turnable: bool = super().perform(engine, action_or_state)
        return turnable


    def render(self, engine: Engine) -> None:
        super().display_main(engine)
        new_cursor_pos: int = engine.terminal_controller.display_inventory(
            engine.player.inventory, self.cursor_index_y)
        self.cursor_index_y = new_cursor_pos


class LevelUpSelectionState(IndexableOptionsState):
    """Handles selection of attributes upon levelup"""

    def handle_input(self,
                     player_input: str) -> Optional[Union[Action, State]]:
        attributes: list[Fighter.AttributeType] = {
            (0, 0): Fighter.AttributeType.POWER,
            (0, 1): Fighter.AttributeType.VITALITY,
            (1, 0): Fighter.AttributeType.AGILITY,
            (1, 1): Fighter.AttributeType.SAGE
        }

        action_or_state: Optional[Union[Action, State]] = None
        # Cannot exit out until attribute is chosen.
        if player_input in MOVE_KEYS:
            x, y = MOVE_KEYS[player_input]
            if x == -1 and y == 0:  # Move cursor up.
                self.cursor_index_x -= 1
            elif x == 0 and y == 1:  # Move cursor right.
                self.cursor_index_y += 1
            elif x == 1 and y == 0:  # Move cursor down.
                self.cursor_index_x += 1
            elif x == 0 and y == -1:  # Move cursor left.
                self.cursor_index_y -= 1
            
            action_or_state = DoNothingAction(self.parent)
        
        # Select attribute.
        elif player_input in CONFIRM_KEYS:
            attribute: Fighter.AttributeType = attributes[
                (self.cursor_index_x, self.cursor_index_y)
            ]
            action_or_state = LevelUpAction(self.parent, attribute)
        
        return action_or_state
    

    def perform(self,
                engine: Engine,
                action_or_state: Union[Action, State]) -> bool:
        turnable: bool = super().perform(engine, action_or_state)

        # An attribute was selected.
        if isinstance(action_or_state, LevelUpAction):
            # Player still has enough experience to level up another time.
            if engine.player.leveler.can_level_up:
                return turnable

            engine.gamestate = ExploreState(self.parent)
        
        return turnable
    

    def render(self, engine: Engine) -> None:
        super().display_main(engine)
        new_cursor_pos: int = \
            engine.terminal_controller.display_levelup_selection(
            engine.player.leveler, engine.player.fighter,
            self.cursor_index_x, self.cursor_index_y
        )
        self.cursor_index_x, self.cursor_index_y = new_cursor_pos

