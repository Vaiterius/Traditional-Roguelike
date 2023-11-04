from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities import Creature
    from ..engine import Engine
from .base_component import BaseComponent
from ..actions import Action, ItemAction
from ..gamestates import State, ConfirmBoxState, Confirmation


class QuestItem(BaseComponent):
    """An item that activates a quest start or end.
    
    For now this will be the main quest item the player needs to win the game
    until we can get a more robust quest system in place to support multiple
    quests.
    """

    def get_action_or_state(self, activator: Creature) -> Union[Action, State]:
        return ItemAction(activator, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Calls a state change to a confirmation display congratulating player
        for winning the game.

        Can be either called from activating the item inside the inventory menu
        or from picking up the item.

        Gamestate should theoretically be in explore or inventory when this is
        called, hopefully.
        """
        confirmation = Confirmation()
        engine.gamestate.confirm_mainquest_finish = confirmation
        engine.gamestate.bypassable = True  # Immediately go back to main menu.
        engine.gamestate = ConfirmBoxState(
            engine.player, engine.gamestate, confirmation,
            "Congrats! Leave?")

        engine.message_log.add("Final quest item found!", color="green")

