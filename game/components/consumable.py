from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities import Creature
    from ..gamestates import State
    from ..engine import Engine
from ..item_types import PotionType
from ..actions import Action, ItemAction
from .base_component import BaseComponent


class Consumable(BaseComponent):
    """An item that can be consumed by a creature"""
    
    def get_action_or_state(self, consumer: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on consuming this item"""
        return ItemAction(consumer, self.owner)

    def perform(self, engine: Engine) -> None:
        """Perform this consumable's action"""
        self.consume()

    def consume(self) -> None:
        """Remove from inventory and consume the item, deleting it"""
        consumer: Creature = self.owner.parent
        if consumer.get_component("inventory") is not None:
            consumer.inventory.remove_item(self.owner)


# TODO disallow entity from drinking if health/magicka is already full.
class RestoreConsumable(Consumable):
    """Restore health or magicka on consumption"""

    def __init__(self, yield_amount: int):
        self._potion_type: PotionType = None
        self._yield_amount = yield_amount
    
    @property
    def potion_type(self) -> PotionType:
        return self._potion_type
    
    @potion_type.setter
    def potion_type(self, new_potion_type: PotionType) -> None:
        self._potion_type = new_potion_type
    
    def perform(self, engine: Engine) -> None:
        consumer: Creature = self.owner.parent
        point_regain_type: str = ""

        # Drink up if health/magicka bar isn't already full.
        if self.potion_type == PotionType.HEALTH:
            if consumer.fighter.health >= consumer.fighter.max_health:
                engine.message_log.add("Health already full!")
                return
            point_regain_type = "hp"
            consumer.fighter.heal(self._yield_amount)
        elif self._potion_type == PotionType.MAGICKA:
            if consumer.fighter.magicka >= consumer.fighter.max_magicka:
                engine.message_log.add("Magicka already full!")
                return
            point_regain_type = "mp"
            consumer.fighter.recharge(self._yield_amount)
        
        engine.message_log.add(
            f"{consumer.name} drinks {self.owner.name} for "
            f"{self._yield_amount} {point_regain_type}!"
        )
        
        return super().perform(engine)

        