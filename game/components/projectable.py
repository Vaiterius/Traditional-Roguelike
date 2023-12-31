from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..engine import Engine
    from ..entities import Creature
    from ..gamestates import State
from ..actions import Action, ItemAction
from .base_component import BaseComponent


class Projectable(BaseComponent):
    """An item that is able to project something at a target cell"""

    def get_action_or_state(self, projector: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on projecting from item"""
        return ItemAction(projector, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Project from item"""
        projector: Creature = self.owner.parent

        engine.message_log.add("The staff fizzes from no charge")
                                                              