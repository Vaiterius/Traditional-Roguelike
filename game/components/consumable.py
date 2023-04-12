from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Item, Creature

from .component import BaseComponent


class Consumable(BaseComponent):
    """An item that can be consumed by a creature"""
    
    def consume(item: Item, creature: Creature) -> None:
        """Perform the consuming action"""
        pass