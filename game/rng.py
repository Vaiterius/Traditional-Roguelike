import random
from typing import Optional, TypeVar

T = TypeVar("T")


class RandomNumberGenerator:

    def __init__(self, seed: Optional[str] = None):
        self._seed = seed

        if self._seed is not None:
            random.seed(self._seed)
    
    @property
    def seed(self) -> str:
        return self._seed
    
    @seed.setter
    def seed(self, new_seed: Optional[str]) -> None:
        """Effectively resets sequence"""
        self._seed = new_seed
        random.seed(new_seed)
    
    # WRAPPERS #

    def random(self) -> float:
        return random.random()
    
    def randint(self, *args, **kwargs) -> int:
        return random.randint(*args, **kwargs)
    
    def choice(self, *args, **kwargs) -> T:
        return random.choice(*args, **kwargs)
    
    def choices(self, *args, **kwargs) -> list[T]:
        return random.choices(*args, **kwargs)
    