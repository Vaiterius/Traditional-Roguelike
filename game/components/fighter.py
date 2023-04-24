from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Creature
from .base_component import BaseComponent
from ..render_order import RenderOrder


def get_modifier_from_attribute(attribute: int) -> int:
    """Table conversion of attribute to modifier"""
    if attribute <= 1:
        return -5
    elif attribute in range(2, 4):
        return -4
    elif attribute in range(4, 6):
        return -3
    elif attribute in range(6, 8):
        return -2
    elif attribute in range(8, 10):
        return -1
    elif attribute in range(10, 12):
        return 0
    elif attribute in range(12, 14):
        return 1
    elif attribute in range(14, 16):
        return 2
    elif attribute in range(16, 18):
        return 3
    elif attribute in range(18, 20):
        return 4
    elif attribute == 20:
        return 5
    else:
        # Add one for every point higher than the max.
        return 5 + (attribute - 20)


class Fighter(BaseComponent):
    """Attaches to an entity that is able to do combat e.g. player, enemies"""

    def __init__(self,
                 health: int,
                 magicka: int,
                 base_damage: int,
                 base_power: int,
                 base_agility: int,
                 base_vitality: int,
                 base_sage: int):
        self.max_health = health
        self._health = health
        self.max_magicka = magicka
        self._magicka = magicka
        self.base_damage = base_damage
        self.crit_damage_bonus: int = 50  # TODO add to data
        
        # Attributes.
        self.base_power = base_power
        self.base_agility = base_agility
        self.base_vitality = base_vitality
        self.base_sage = base_sage
        
        # Combat chances.
        self.hit_chance: int = 50
        self.crit_chance: int = 5

    
    # HEALTH #
    
    @property
    def is_dead(self) -> bool:
        return self._health <= 0
    
    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, new_health: int) -> None:
        # New HP cannot be lower than 0 or higher than max HP.
        self._health = max(0, min(self.max_health, new_health))
        if self.is_dead:
            self.die()
    
    
    # MAGICKA #
    
    @property
    def is_drained(self) -> bool:
        return self._magicka
    
    @property
    def magicka(self) -> int:
        return self._magicka
    
    @magicka.setter
    def magicka(self, new_magicka: int) -> int:
        # New MP cannot be lower than 0 or higher than max MP.
        self._magicka = max(0, min(self.max_magicka, new_magicka))


    # COMBAT #
    
    def heal(self, amount: int) -> None:
        """Recover HP by some amount"""
        self.health += amount
    
    
    def recharge(self, amount: int) -> None:
        """Recover MP by some amount"""
        self.magicka += amount
    
    
    def get_modified_damage(self) -> int:
        """Get modified base damage with attack-based skill points applied"""
        return self.base_damage
    
    
    def take_damage(self, amount: int) -> None:
        """Set damage taken with defense-based skill points applied"""
        self.health -= amount
        if self.is_dead:
            self.die()
    
    
    def die(self) -> None:
        """Creature dies. RIP bozo."""
        creature: Creature = self.owner

        if creature.get_component("ai") is not None:
            creature.ai = None
        creature.blocking = False
        creature.char = "%"
        creature.color = "blood_red"
        creature.name = f"Remains of {creature.og_name}"
        creature.render_order = RenderOrder.CORPSE

