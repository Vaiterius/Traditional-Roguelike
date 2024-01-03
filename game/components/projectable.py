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

    def __init__(self, uses: int, magicka_cost: int):
        self._uses_left = uses
        self._magicka_cost = magicka_cost
    
    @property
    def uses_left(self) -> int:
        return self._uses_left
    
    @property
    def magicka_cost(self) -> int:
        return self._magicka_cost
    
    def expend_use(self) -> None:
        self._uses_left -= 1

    def get_action_or_state(self, projector: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on projecting from item"""
        return ItemAction(projector, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Project from item"""
        pass


class LightningProjectable(Projectable):
    """An item that shoots out a powerful burst of lightning"""

    def __init__(self, uses: int, magicka_cost: int, damage: int):
        super().__init__(uses, magicka_cost)
        self._damage = damage
    
    def perform(self, engine: Engine) -> None:
        projector: Creature = self.owner.parent

        engine.message_log.add("The staff shoots out a bolt of lightning towards the ceiling")

        self.expend_use()


class HealingProjectable(Projectable):
    """An item that shoots out a healing orb"""

    def __init__(self, uses: int, magicka_cost: int, heal: int):
        super().__init__(uses, magicka_cost)
        self._heal = heal
    
    def perform(self, engine: Engine) -> None:
        projector: Creature = self.owner.parent

        engine.message_log.add("The staff sends out an orb towards the ceiling")

        self.expend_use()

                                                              