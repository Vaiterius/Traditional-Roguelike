import curses

from game import __version__
import game.data.config as config
from game.engine import Engine
from game.terminal_control import TerminalController
from game.gamestates import MainMenuState
from game.save_handling import Save
from game.entities import Creature


def main(screen: curses.initscr):
    # curses frontend to handle display and input handling.
    terminal_controller = TerminalController(
        screen=screen,
        floor_dimensions=config.FLOOR_DIMENSIONS
    )
    # Filler data to start the engine.
    dummy: Creature = Creature(-1, -1, "", "", "", None, 69, -1)
    save = Save(
        slot_index=-1, path=None, data={"dummy": dummy}, metadata={"version": __version__})
    gamestate = MainMenuState(dummy)
    
    engine = Engine(
        screen,
        save,
        terminal_controller,
        gamestate
    )
    engine.run()


if "__main__" == __name__:
    curses.wrapper(main)
