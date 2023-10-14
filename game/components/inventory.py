from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ..entities import Item, Weapon, Armor
    from ..item_types import ArmorType
from .base_component import BaseComponent


# TODO split inventory list by item type (e.g. weapons, armor)
class Inventory(BaseComponent):
    """Inventory space for player weapons, armor, potions, and other items"""
    
    def __init__(self, num_slots: int):
        self.max_slots = num_slots
        self.items: list[Item] = []

        self.equipped_weapon: Optional[Weapon] = None
        self.equipped_head_armor: Optional[Armor] = None
        self.equipped_torso_armor: Optional[Armor] = None
        self.equipped_leg_armor: Optional[Armor] = None
    
    def __str__(self):
        return "Inventory: [" + ", ".join(self.items) + "]"

    @property
    def size(self) -> int:
        """Return number of items in the inventory"""
        return len(self.items)
    
    @property
    def weapon(self) -> Optional[Weapon]:
        return self.equip_weapon
    
    @property
    def head_armor(self) -> Optional[Armor]:
        return self.equipped_head_armor
    
    @property
    def torso_armor(self) -> Optional[Armor]:
        return self.equipped_torso_armor
    
    @property
    def leg_Armor(self) -> Optional[Armor]:
        return self.equipped_leg_armor
    

    # ITEM MANAGEMENT #
    
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
    
    def equip(self, item: Union[Weapon, Armor]) -> None:
        """Equip an item to its right slot"""
        if isinstance(item, Weapon):
            self.equip_weapon(item)
        elif isinstance(item, Armor):
            self.equip_armor(item)
    

    # WEAPON MANAGEMENT #

    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a weapon if one is not already equipped"""
        self.equipped_weapon = weapon


    # ARMOR MANAGEMENT #

    def equip_armor(self, armor: Armor) -> None:
        """Equip armor if slot is not already filled"""
        if armor.armor_type == ArmorType.HEAD:
            self.equipped_head_armor = armor
        elif armor.armor_type == ArmorType.TORSO:
            self.equipped_torso_armor = armor
        elif armor.armor_type == ArmorType.LEGS:
            self.equipped_leg_armor = armor

