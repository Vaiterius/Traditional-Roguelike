"""
Power:
------
✔️(BASE 5pts) increased melee damage (+1pt per point)
(BASE 0%) increased bow projectile damage (+2% per point)
✔️(BASE 5%) increased chance to knock out (+3% per point)
✔️(BASE 50%) increased critical hit damage bonus (+5% per point)

Agility:
--------
✔️(BASE 75%) increased melee hit chance (+2% per point)
(BASE 75%) increased projectile hit chance (+2% per point)
✔️(BASE 5%) increased critical hit chance (+1% per point)
✔️(BASE 10%) increased double hit chance (+3% per point)

Vitality:
---------
✔️(BASE 50hp) increased max health points (+2hp per point, +3hp per 5 points)
(BASE 1hp) increased health regeneration per 10 turns (+0.5hp per point)
(BASE 10hp) health potions yield more points (+1hp per point)

SAGE:
-----
✔️(BASE 50mp) increased max magicka points (+2mp per point, +3mp per point)
(BASE 1mp) increased magicka regeneration per 10 turns (+0.5mp per point)
(BASE 0%) spell effects are stronger (+5% per point)
(BASE 10mp) magicka potions yield more points (+1mp per point)
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Creature
from .base_component import BaseComponent
from ..render_order import RenderOrder


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
        self._max_health = health
        self._max_magicka = magicka
        self._health = health
        self._magicka = magicka
        self._base_damage = base_damage
        
        # Attributes.
        self._base_power = base_power
        self._base_agility = base_agility
        self._base_vitality = base_vitality
        self._base_sage = base_sage
        
        # TODO add to data file.
        # Combat chances.
        self._hit_chance: float = 0.75
        self._knockout_chance: float = 0.05
        self._crit_chance: float = 0.01
        self._crit_damage_bonus: float = 0.50
        self._double_hit_chance: float = 0.05

    
    # HEALTH #
    
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
    
    @property
    def max_health(self) -> int:
        """Max health based on vitality level"""
        base_max: int = self._max_health
        for curr_point in range(0, self.vitality - 1):
            if curr_point % 5 == 0:  
                base_max += 3  # Every 5 points.
            else:  
                base_max += 2  # Every 1 point.
        return base_max
    
    @property
    def health(self) -> int:
        return self._health
    
    def heal(self, amount: int) -> None:
        """Recover HP by some amount"""
        self.health += amount
    
    @health.setter
    def health(self, new_health: int) -> None:
        # New HP cannot be lower than 0 or higher than max HP.
        self._health = max(0, min(self.max_health, new_health))
        if self.is_dead:
            self.die()
    
    
    # MAGICKA #
    
    @property
    def is_drained(self) -> bool:
        return self.magicka <= 0
    
    @property
    def max_magicka(self) -> int:
        """Max magicka based on sage level"""
        base_max: int = self._max_magicka
        for curr_point in range(0, self.sage - 1):
            if curr_point % 5 == 0:  
                base_max += 3  # Every 5 points.
            else:  
                base_max += 2  # Every 1 point.
        return base_max
    
    @property
    def magicka(self) -> int:
        return self._magicka
    
    def recharge(self, amount: int) -> None:
        """Recover MP by some amount"""
        self.magicka += amount
    
    @magicka.setter
    def magicka(self, new_magicka: int) -> None:
        # New MP cannot be lower than 0 or higher than max MP.
        self.magicka = max(0, min(self.max_magicka, new_magicka))
    

    # ATTRIBUTES #

    # POWER.
    @property
    def power(self) -> int:
        return self._base_power
    
    @power.setter
    def power(self, new_power: int) -> None:
        self.power = max(1, new_power)
    
    # AGILITY.
    @property
    def agility(self) -> int:
        return self._base_agility
    
    @agility.setter
    def agility(self, new_agility: int) -> None:
        self.agility = max(1, new_agility)
    
    # VITALITY.
    @property
    def vitality(self) -> int:
        return self._base_vitality
    
    @vitality.setter
    def vitality(self, new_vitality: int) -> None:
        self.vitality = max(1, new_vitality)

    # SAGE.
    @property
    def sage(self) -> int:
        return self._base_sage
    
    @sage.setter
    def sage(self, new_sage: int) -> None:
        self.sage = max(1, new_sage)


    # COMBAT #

    # TODO take into account melee/ranged weapon player is holding.
    @property
    def damage(self) -> int:
        """Get modified damage from power level"""
        return self._base_damage + (self.power - 1)
    
    # TODO incorporate this to the above, with an condition check of crit success.
    @property
    def critical_damage(self) -> int:
        """Strengthened modified damage due to critical hit success"""
        modified_bonus: float = self._crit_damage_bonus + (self.power * 0.05)
        return round(self.damage * (1.00 + modified_bonus))
    
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
    

    # COMBAT CHANCES #

    # MELEE HIT CHANCE.
    @property
    def hit_chance(self) -> float:
        return self._hit_chance + (self.agility * 0.02)

    def check_hit_success(self) -> bool:
        """Attempt to hit opponent succeeds or not"""
        return self.hit_chance <= random.random()
    
    # CRITICAL HIT CHANCE.
    @property
    def critical_hit_chance(self) -> float:
        return self._crit_chance + (self.agility * 0.01)
    
    def check_critical_hit_success(self) -> bool:
        """A hit that turns out to be a critical hit"""
        return self.critical_hit_chance <= random.random()
    
    # KNOCKOUT CHANCE.
    @property
    def knockout_chance(self) -> float:
        return self._knockout_chance + (self.power * 0.03)
    
    def check_knockout_success(self) -> bool:
        """A hit that knocks out the target creature"""
        return self.knockout_chance <= random.random()
    
    # DOUBLE HIT CHANCE.
    @property
    def double_hit_chance(self) -> float:
        return self._double_hit_chance + (self.agility * 0.03)
    
    def check_double_hit_success(self) -> bool:
        """A hit attempt that strikes the target creature twice"""
        return self.double_hit_chance <= random.random()
    
