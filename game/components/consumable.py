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


class RestoreConsumable(Consumable):
    """Restore some attribute on consumption"""
    
    def __init__(self, yield_amount: int):
        self.yield_amount = yield_amount


class RestoreHealthConsumable(RestoreConsumable):
    """Restore health on consumption"""
    
    def perform(self, engine: Engine) -> None:
        consumer: Creature = self.owner.parent
        
        consumer.set_hp(consumer.hp + self.yield_amount)
        engine.message_log.add(
            f"{consumer.name} drinks {self.owner.name} for "
            f"{self.yield_amount} hp!"
        )
        
        return super().perform(engine)


class RestoreMagickaConsumable(RestoreConsumable):
    """Restore magicka on consumption"""

    def perform(self, engine: Engine) -> None:
        consumer: Creature = self.owner.parent
        
        # Only creatures that are able to wield magic can gain the effect.
        if not consumer.get_component("mp"):
            engine.message_log.add(
                f"{consumer.name} attempts to drink a potion of magicka... "
                "but to no effect."
                )
            return super().perform(engine)  # Consume it as well.
        
        consumer.set_mp(consumer.mp + self.yield_amount)
        engine.message_log.add(
            f"{consumer.name} drinks {self.owner.name} for "
            f"{self.yield_amount} hp!"
        )
        
        return super().perform(engine)
        
        