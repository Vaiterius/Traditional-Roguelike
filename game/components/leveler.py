from __future__ import annotations

from typing import TYPE_CHECKING
from .base_component import BaseComponent

if TYPE_CHECKING:
    from .fighter import Fighter


def experience_needed(level: int) -> int:
    """Linear growth formula (for now)"""
    return round((5 * level) + 5)


class Leveler(BaseComponent):
    """System for leveling up entities' stats"""

    def __init__(self, start_level: int = 1, base_drop_amount: int = 5):
        self._start_level = start_level
        self._current_level = start_level

        # Scale drop amount based on starting level.
        DROP_SCALER: float = 1.5
        self._base_drop_amount = round(
            base_drop_amount + ((start_level - 1) * DROP_SCALER))

        self._total_experience: int = 0
        self._current_experience: int = 0
    
    @property
    def level(self) -> int:
        return self._current_level
    
    @property
    def can_level_up(self) -> bool:
        return self.experience >= experience_needed(self.level + 1)
    
    @property
    def experience(self) -> int:
        return self._current_experience
    
    @property
    def total_experience(self) -> int:
        return self._total_experience
    
    @property
    def experience_left_to_level_up(self) -> int:
        return experience_needed(self._current_level + 1) - self.experience
    
    @property
    def experience_drop(self) -> int:
        return self._base_drop_amount
    
    def absorb(self, incoming_experience: int) -> None:
        self._current_experience += incoming_experience
        self._total_experience += incoming_experience
    
    def level_up(self) -> None:
        self._current_experience -= experience_needed(self._current_level + 1)
        self._current_level += 1
    
    def increase_power(self) -> None:
        self.owner.get_component("fighter").power += 1
    
    def increase_agility(self) -> None:
        self.owner.get_component("fighter").agility += 1
    
    def increase_vitality(self) -> None:
        self.owner.get_component("fighter").vitality += 1
    
    def increase_sage(self) -> None:
        self.owner.get_component("fighter").sage += 1
    
    