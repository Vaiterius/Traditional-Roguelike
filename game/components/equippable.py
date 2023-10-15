from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from .inventory import Inventory
    from ..entities import Creature
    from ..gamestates import State
    from ..engine import Engine
from ..actions import Action, ItemAction
from .base_component import BaseComponent


class Equippable(BaseComponent):
    """An item that can be equipped in a creature's inventory"""

    def get_action_or_state(self, wielder: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on equipping this item"""
        return ItemAction(wielder, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Equip this item"""
        equipper: Creature = self.owner.parent
        inventory: Optional[Inventory] = equipper.get_component("inventory")

        if inventory is None:
            return
        
        # Toggle equipping.
        if inventory.is_equipped(self.owner):
            inventory.unequip(self.owner)
            engine.message_log.add(f"{self.owner.name} has been unequipped")
        else:
            inventory.equip(self.owner)
            engine.message_log.add(f"{self.owner.name} has been equipped")


class Wieldable(Equippable):
    """An item that can be held by a creature"""

    def __init__(self, damage_bonus: int):
        self._damage_bonus = damage_bonus

    @property
    def damage_bonus(self) -> int:
        return self._damage_bonus


class Wearable(Equippable):
    """An item that can be worn by a creature"""

    def __init__(self, damage_reduction: int, coverage: int):
        self._damage_reduction = damage_reduction
        self._coverage = coverage
    
    @property
    def damage_reduction(self) -> float:
        return self._damage_reduction / 100
    
    @property
    def coverage(self) -> float:
        return self._coverage

