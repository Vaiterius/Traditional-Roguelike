from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import Engine
    from ..entities import Entity
from ..actions import Action, BumpAction


class BaseComponent:
    """A basic component, lives in an entity's component pack"""
    owner: Entity


class BaseAI(Action, BaseComponent):

    """Basic AI that gets a path to a cell"""
    DIRECTIONS = {
        "NORTHWEST": (-1, -1),
        "NORTH": (-1, 0),
        "NORTHEAST": (-1, 1),
        "WEST": (0, -1),
        "EAST": (0, 1),
        "SOUTHWEST": (1, -1),
        "SOUTH": (1, 0),
        "SOUTHEAST": (1, 1)
    }

    def perform(self, engine: Engine):
        pass

    def get_path_to(self, engine: Engine, x: int, y: int) -> list[tuple[int, int]]:
        pass


class WanderingAI(BaseAI):
    """AI that wanders the floors aimlessly"""
    CHANCE_TO_WALK: float = 0.75

    def perform(self, engine: Engine):
        # Decide if creature wants to randomly walk to a tile.
        to_walk_or_not_to_walk_that_is_the_question: bool = random.random()
        if to_walk_or_not_to_walk_that_is_the_question >= self.CHANCE_TO_WALK:
            # Pick a random, valid direction to walk to.
            dx, dy = random.choice(list(self.DIRECTIONS.values()))
            
            # Walk to that tile if it is not blocked by a blocking entity.
            BumpAction(self.owner, dx, dy).perform(engine)


class HostileEnemyAI(BaseAI):
    """AI that targets and fights the playe; pseudo-pathfinding algorithm"""

    def perform(self):
        pass

