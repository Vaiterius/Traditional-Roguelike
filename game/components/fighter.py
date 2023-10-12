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
(BASE 60%) increased projectile hit chance (+3% per point)
✔️(BASE 5%) increased critical hit chance (+1% per point)
✔️(BASE 10%) increased double hit chance (+3% per point)

Vitality:
---------
✔️(BASE 50hp) increased max health points (+2hp per point, +3hp per 5 points)
(BASE 1hp) increased health regeneration per 10 turns (+0.5hp per point)
(BASE 10hp) health potions yield more points (+2hp per point)

SAGE:
-----
✔️(BASE 50mp) increased max magicka points (+2mp per point, +3mp per point)
(BASE 1mp) increased magicka regeneration per 10 turns (+0.5mp per point)
(BASE 0%) spell attacks/effects are stronger (+5% per point)
(BASE 10mp) magicka potions yield more points (+1mp per point)
"""

from __future__ import annotations

import random
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Creature
from .base_component import BaseComponent
from ..render_order import RenderOrder


# TODO turn these static methods into decorators for fighter properties?
class StatModifier:
    """Util functions that modify combat bonuses based on attribute level"""
    JUICE_PER_3_POINTS = 3
    JUICE_PER_POINT = 2
    DAMAGE_PER_POINT = 1
    HIT_CHANCE_PER_POINT = 0.02
    CRITICAL_HIT_CHANCE_PER_POINT = 0.01
    CRITICAL_HIT_DAMAGE_BONUS_PER_POINT = 0.05
    KNOCKOUT_CHANCE_PER_POINT = 0.03
    DOUBLE_HIT_CHANCE_PER_POINT = 0.03
    
    @staticmethod
    def add_max_points(attribute: int) -> int:
        """Add points to max health or magicka.
        
        `attribute` is either vitality or sage.
        """
        extra_points = 0
        for current_point in range(0, attribute - 1):
            if current_point % 3 == 0:
                extra_points += StatModifier.JUICE_PER_3_POINTS
            else:
                extra_points += StatModifier.JUICE_PER_POINT
        return extra_points
    
    @staticmethod
    def add_damage(power: int) -> int:
        """1 damage bonus for every power level"""
        return power - 1  # Offset, level 1 is base (+0)
    
    @staticmethod
    def add_hit_chance(agility: int) -> float:
        """2% bonus for every agility level"""
        return agility * StatModifier.HIT_CHANCE_PER_POINT
    
    @staticmethod
    def add_critical_hit_chance(agility: int) -> float:
        """1% bonus for every agility level"""
        return agility * StatModifier.CRITICAL_HIT_CHANCE_PER_POINT
    
    @staticmethod
    def add_critical_hit_damage_bonus(power: int) -> float:
        """5% bonus for every power level"""
        return power * StatModifier.CRITICAL_HIT_DAMAGE_BONUS_PER_POINT
    
    @staticmethod
    def add_knockout_chance(power: int) -> float:
        """3% bonus for every power level"""
        return power * StatModifier.KNOCKOUT_CHANCE_PER_POINT
    
    @staticmethod
    def add_double_hit_chance(agility: int) -> float:
        """3% bonus for every agility level"""
        return agility * StatModifier.DOUBLE_HIT_CHANCE_PER_POINT


class Fighter(BaseComponent):
    """Attaches to an entity that is able to do combat e.g. player, enemies"""

    class AttributeType(Enum):
        """The set of attributes a fighter entity can have"""
        POWER = auto()
        AGILITY = auto()
        VITALITY = auto()
        SAGE = auto()

    def __init__(self,
                 base_health: int,
                 base_magicka: int,
                 base_damage: int,
                 base_power: int,
                 base_agility: int,
                 base_vitality: int,
                 base_sage: int):
        self._max_health = base_health
        self._max_magicka = base_magicka
        self._health = base_health
        self._magicka = base_magicka
        self._damage = base_damage
        
        # Attributes.
        self._power = base_power
        self._agility = base_agility
        self._vitality = base_vitality
        self._sage = base_sage
        
        # TODO add to data file?
        # Combat chances.
        self._HIT_CHANCE: float = 0.75
        self._KNOCKOUT_CHANCE: float = 0.05
        self._CRITICAL_CHANCE: float = 0.01
        self._CRITICAL_DAMAGE_BONUS: float = 0.50
        self._DOUBLE_HIT_CHANCE: float = 0.05

        # Update and recalculate after modifiers.
        self._health = self.max_health
        self._magicka = self.max_magicka

    
    # HEALTH #
    
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
    
    @property
    def max_health(self) -> int:
        """Max health based on vitality level"""
        return self._max_health + \
            StatModifier.add_max_points(self.vitality)
    
    @property
    def health(self) -> int:
        return self._health
    
    def heal(self, amount: int) -> None:
        """Recover HP by some amount. Will call health setter."""
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
        return self._max_magicka + StatModifier.add_max_points(self.sage)
    
    @property
    def magicka(self) -> int:
        return self._magicka
    
    def recharge(self, amount: int) -> None:
        """Recover MP by some amount. Will call magicka setter."""
        self.magicka += amount
    
    @magicka.setter
    def magicka(self, new_magicka: int) -> None:
        # New MP cannot be lower than 0 or higher than max MP.
        self._magicka = max(0, min(self.max_magicka, new_magicka))
    

    # TODO provide tests
    # ATTRIBUTES #

    # POWER.
    @property
    def power(self) -> int:
        return self._power
    
    @power.setter
    def power(self, new_power: int) -> None:
        self._power = max(1, new_power)
    
    # AGILITY.
    @property
    def agility(self) -> int:
        return self._agility
    
    @agility.setter
    def agility(self, new_agility: int) -> None:
        self._agility = max(1, new_agility)
    
    # VITALITY.
    @property
    def vitality(self) -> int:
        return self._vitality
    
    @vitality.setter
    def vitality(self, new_vitality: int) -> None:
        self._vitality = max(1, new_vitality)

    # SAGE.
    @property
    def sage(self) -> int:
        return self._sage
    
    @sage.setter
    def sage(self, new_sage: int) -> None:
        self._sage = max(1, new_sage)


    # COMBAT #

    # TODO take into account melee/ranged weapon player is holding.
    @property
    def damage(self) -> int:
        """Get modified damage from power level"""
        return self._damage + StatModifier.add_damage(self.power)
    
    # TODO incorporate this to the above, with a condition check of crit success.
    @property
    def critical_damage(self) -> int:
        """Strengthened modified damage due to critical hit success"""
        return round(self.damage * (1.00 + self.critical_hit_damage_bonus))
    
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
        return self._HIT_CHANCE + \
            StatModifier.add_hit_chance(self.agility)

    def check_hit_success(self) -> bool:
        """Attempt to hit opponent succeeds or not"""
        return self.hit_chance <= random.random()
    
    # CRITICAL HIT CHANCE.
    @property
    def critical_hit_chance(self) -> float:
        return self._CRITICAL_CHANCE + \
            StatModifier.add_critical_hit_chance(self.agility)
    
    @property
    def critical_hit_damage_bonus(self) -> float:
        return self._CRITICAL_DAMAGE_BONUS + \
            StatModifier.add_critical_hit_damage_bonus(self.power)
    
    def check_critical_hit_success(self) -> bool:
        """A hit that turns out to be a critical hit"""
        return self.critical_hit_chance <= random.random()
    
    # KNOCKOUT CHANCE.
    @property
    def knockout_chance(self) -> float:
        return self._KNOCKOUT_CHANCE + \
            StatModifier.add_knockout_chance(self.power)
    
    def check_knockout_success(self) -> bool:
        """A hit that knocks out the target creature"""
        return self.knockout_chance <= random.random()
    
    # DOUBLE HIT CHANCE.
    @property
    def double_hit_chance(self) -> float:
        return self._DOUBLE_HIT_CHANCE + \
            StatModifier.add_double_hit_chance(self.agility)
    
    def check_double_hit_success(self) -> bool:
        """A hit attempt that strikes the target creature twice"""
        return self.double_hit_chance <= random.random()
    
