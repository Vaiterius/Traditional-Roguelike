"""
Files that include the RNG for tracking purposes:
game/actions.py
game/components/ai.py
game/components/fighter.py
game/components/leveler.py
game/dungeon/dungeon.py
game/dungeon/floor.py
game/dungeon/room.py
game/engine.py
game/save_handling.py
game/spawner.py
game/terminal_control.py
"""

import random
from typing import Optional, TypeVar

T = TypeVar("T")


class RandomNumberGenerator:
    """Provide a seed for anything procedurally-generated.
    
    If no seed was passed in, it will be random.
    """

    def __init__(self, seed: Optional[str] = None):
        self._global_seed = seed

        if self._global_seed is not None:
            random.seed(self._global_seed)
    
    @property
    def seed(self) -> str:
        return self._global_seed
    
    @seed.setter
    def seed(self, new_seed: Optional[str]) -> None:
        """Reset sequence"""
        random.seed(new_seed)
    
    def with_subseed(self, appendage: str) -> None:
        """For specific types of generations e.g. rooms and entity spawns"""
        if self.seed is not None:
            self.seed = self._global_seed + appendage
    
    # WRAPPERS #

    def random(self) -> float:
        return random.random()
    
    def randint(self, *args, **kwargs) -> int:
        return random.randint(*args, **kwargs)
    
    def choice(self, *args, **kwargs) -> T:
        return random.choice(*args, **kwargs)
    
    def choices(self, *args, **kwargs) -> list[T]:
        return random.choices(*args, **kwargs)
    