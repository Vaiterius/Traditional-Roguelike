from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..entities import Item
from .base_component import BaseComponent


# TODO split inventory list by item type (e.g. weapons, armor)
class Inventory(BaseComponent):
    """Inventory space for player weapons, potions, and other items"""
    
    def __init__(self, num_slots: int):
        self.max_slots = num_slots
        self.items: list[Item] = []
    
    def __str__(self):
        return "Inventory: [" + ", ".join(self.items) + "]"

    @property
    def size(self) -> int:
        """Return number of items in the inventory"""
        return len(self.items)
    
    
    def add_item(self, item: Item) -> None:
        """Add an item to the inventory"""
        if self.size >= self.max_slots:
            return
        self.items.append(item)
    
    
    def add_items(self, items: list[Item]) -> Optional[Item]:
        """
        Add a list of items to the inventory if space is sufficient.
        Return the remaining items that could not be added otherwise.
        """
        for i in range(len(items)):
            if self.size >= self.max_slots:
                return items
            self.items.append(items.pop())
    
    
    def get_item(self, item_idx: int) -> Optional[Item]:
        """Retrieve an item from the inventory by list index"""
        try:
            item: Item = self.items[item_idx]
        except IndexError:
            return None
        return item
    
    
    def remove_item(self, item: Item) -> Optional[Item]:
        """Remove a specified item from the inventory"""
        try:
            self.items.remove(item)
        except ValueError:
            return None
        return item