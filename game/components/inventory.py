from typing import Optional, Union

from ..entities import Item, Weapon, Armor
from ..item_types import ArmorType
from .base_component import BaseComponent


class Inventory(BaseComponent):
    """
    Inventory space and management for weapons, armor, potions, and other items
    """
    
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
        return self.equipped_weapon
    
    @property
    def head_armor(self) -> Optional[Armor]:
        return self.equipped_head_armor
    
    @property
    def torso_armor(self) -> Optional[Armor]:
        return self.equipped_torso_armor
    
    @property
    def leg_armor(self) -> Optional[Armor]:
        return self.equipped_leg_armor
    
    @property
    def damage_bonus(self) -> int:
        damage_bonus = 0
        if self.weapon and self.weapon.get_component("equippable"):
            damage_bonus += self.weapon.equippable.damage_bonus
        return damage_bonus
    
    @property
    def damage_reduction(self) -> float:
        damage_reduction = 0.00

        if self.head_armor and self.head_armor.get_component("equippable"):
            damage_reduction += \
                self.head_armor.equippable.damage_reduction
        if self.torso_armor and self.torso_armor.get_component("equippable"):
            damage_reduction += \
                self.torso_armor.equippable.damage_reduction
        if self.leg_armor and self.leg_armor.get_component("equippable"):
            damage_reduction += \
                self.leg_armor.equippable.damage_reduction
        
        return damage_reduction
    
    @property
    def has_quest_item(self) -> bool:
        """Check if player has the relic in their inventory"""
        for item in self.items:
            if item.get_component("relic") is not None:
                return True
        return False
    

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
        for _ in range(len(items)):
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
    
    def unequip(self, item: Union[Weapon, Armor]) -> None:
        if isinstance(item, Weapon):
            self.unequip_weapon(item)
        elif isinstance(item, Armor):
            self.unequip_armor(item)
    
    def is_equipped(self, item: Union[Weapon, Armor]) -> bool:
        return item in {
            self.equipped_weapon,
            self.equipped_head_armor,
            self.equipped_torso_armor,
            self.equipped_leg_armor
        }
    
    # def count_instances_of(self, item_class: Item) -> int:
    #     """Get the number of occurrences that are instances of a given class"""
    #     count: int = 0
    #     for item in self.items:
    #         if isinstance(item, item_class):
    #             count += 1
    #     return count

    def count_instances_with_component(self, component_name: str) -> int:
        """Get the number of occurrences that have the given component"""
        count: int = 0
        for item in self.items:
            if item.get_component(component_name) is not None:
                count += 1
        return count
    

    # WEAPON MANAGEMENT #

    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a weapon if one is not already equipped"""
        self.equipped_weapon = weapon
    
    def unequip_weapon(self, weapon: Weapon) -> None:
        if self.equipped_weapon == weapon:
            self.equipped_weapon = None


    # ARMOR MANAGEMENT #

    def equip_armor(self, armor: Armor) -> None:
        """Equip armor if slot is not already filled"""
        if armor.armor_type == ArmorType.HEAD:
            self.equipped_head_armor = armor
        elif armor.armor_type == ArmorType.TORSO:
            self.equipped_torso_armor = armor
        elif armor.armor_type == ArmorType.LEGS:
            self.equipped_leg_armor = armor
    
    def unequip_armor(self, armor: Armor) -> None:
        if self.equipped_head_armor == armor:
            self.equipped_head_armor = None
        elif self.equipped_torso_armor == armor:
            self.equipped_torso_armor = None
        elif self.equipped_leg_armor == armor:
            self.equipped_leg_armor = None

