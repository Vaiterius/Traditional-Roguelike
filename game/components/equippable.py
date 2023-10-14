from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities import Creature
    from ..gamestates import State
    from ..engine import Engine
from ..actions import Action, ItemAction
from .base_component import BaseComponent


class Equippable(BaseComponent):
    """An item that can be equipped in a creature's inventory"""

    def get_action_or_state(self, wielder: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on wielding this item"""
        return ItemAction(wielder, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Equip this item"""
        self.equip()
        engine.message_log.add(f"{self.owner.name} has been equipped")
    
    def equip(self) -> None:
        """Set as equipped inside inventory"""
        equipper: Creature = self.owner.parent
        if equipper.get_component("inventory"):
            equipper.inventory.equip(self.owner)


# class Wieldable(Equippable):
#     """An item that can be wielded by a creature"""


# class Wearable(Equippable):
#     """An item that can be worn by a creature"""

