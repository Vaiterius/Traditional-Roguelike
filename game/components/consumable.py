from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities import Creature
    from ..gamestates import State
    from ..engine import Engine
from ..actions import Action, ItemAction
from .component import BaseComponent


class Consumable(BaseComponent):
    """An item that can be consumed by a creature"""
    
    
    def get_action_or_state(self, consumer: Creature) -> Union[Action, State]:
        """
        Get an action or state to be performed on using consuming this item
        """
        return ItemAction(consumer, self.owner)
    
    
    def perform(self, engine: Engine) -> None:
        """Perform this consumable's action"""
        self.consume()
    
    
    def consume(self) -> None:
        """Remove from inventory and consume the item, deleting it"""
        consumer: Creature = self.owner.parent
        if consumer.get_component("inventory") is not None:
            consumer.inventory.remove_item(self.owner)


class HealingConsumable(Consumable):
    """Apply healing effects on consumption"""
    
    def perform(self, engine: Engine) -> None:
        
        # TODO have the item heal its consumer.
        
        return super().perform(engine)
        
        