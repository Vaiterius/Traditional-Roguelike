from __future__ import annotations

from typing import TYPE_CHECKING
from .base_component import BaseComponent

# if TYPE_CHECKING:
    # from .fighter import Fighter
from .fighter import Fighter


def experience_needed_for_level(level: int) -> int:
    """Linear growth formula (for now)"""
    if level < 2:
        return 0
    return round((5 * (level - 1)) + 5)


class Leveler(BaseComponent):
    """System for leveling up entities' stats"""

    def __init__(self, start_level: int = 1, base_drop_amount: int = 5):
        self._start_level = start_level
        self._current_level = start_level
        self._base_drop_amount = base_drop_amount

        self._total_experience: int = 0
        self._current_experience: int = 0


    # LEVELING #
    
    @property
    def level(self) -> int:
        return self._current_level
    
    @property
    def can_level_up(self) -> bool:
        return self.experience >= experience_needed_for_level(self.level + 1)
    
    def level_up(self) -> None:
        """Expend experience points towards leveling up, leaving leftovers"""
        self._current_experience -= experience_needed_for_level(self.level + 1)
        self._current_level += 1


    # EXPERIENCE #
    
    @property
    def experience(self) -> int:
        return self._current_experience
    
    @property
    def total_experience(self) -> int:
        return self._total_experience
    
    @property
    def experience_left_to_level_up(self) -> int:
        return experience_needed_for_level(
            self._current_level + 1) - self.experience
    
    @property
    def experience_drop(self) -> int:
        """Scale drop experience based on level"""
        DROP_SCALER: float = 1.5
        return round(self._base_drop_amount + ((self.level - 1) * DROP_SCALER))
    
    def absorb(self, incoming_experience: int) -> None:
        if incoming_experience < 0:
            incoming_experience = 0
        self._current_experience += round(incoming_experience)
        self._total_experience += round(incoming_experience)


    # ATTRIBUTE LEVELING #
    
    def increment_attribute(self, attribute: Fighter.AttributeType) -> None:
        if attribute == Fighter.AttributeType.POWER:
            self.owner.fighter.power += 1
        elif attribute == Fighter.AttributeType.AGILITY:
            self.owner.fighter.agility += 1
        elif attribute == Fighter.AttributeType.VITALITY:
            self.owner.fighter.vitality += 1
        elif attribute == Fighter.AttributeType.SAGE:
            self.owner.fighter.sage += 1
    
    