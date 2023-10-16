from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from game.engine import Engine

if TYPE_CHECKING:
    from ..engine import Engine
    from ..entities import Entity
    from .leveler import Leveler
    from ..dungeon.floor import Floor
from .fighter import Fighter
from .base_component import BaseComponent
from ..actions import Action, BumpAction
from ..pathfinding import bresenham_path_to, a_star_path_to


class BaseAI(Action, BaseComponent):
    """Basic AI that gets a path to a cell"""
    AGRO_RANGE: int = 8

    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.entity = entity
        self.agro = False


    def perform(self, engine: Engine):
        # Check for available level up.
        leveler: Leveler = self.entity.get_component("leveler")
        fighter: Fighter = self.entity.get_component("fighter")

        if leveler is None or fighter is None:
            return
        
        # Randomly assign an attribute point, though probably never needed.
        while leveler.can_level_up:
            leveler.increment_attribute(leveler.get_random_attribute())
            leveler.level_up()


    def update_agro_status(
            self, engine: Engine, paths: list[tuple[int, int]]) -> None:
        """
        Check each turn if enemy is in agro proximity to player and there is no
        boundary between them
        """
        player_x, player_y = engine.player.x, engine.player.y
        distance_from_player: float = math.dist(
            (player_x, player_y),
            (self.entity.x, self.entity.y)
        )
        
        # Checking for blocked tiles in enemy paths.
        tiles = engine.dungeon.current_floor.tiles
        blocked: bool = any([not tiles[x][y].walkable for x,y in paths])

        if distance_from_player <= self.AGRO_RANGE and not blocked:
            self.agro = True
        else:
            self.agro = False


    def get_path_to(self, x: int, y: int) -> list[tuple[int, int]]:
        """Get a set coordinate points following a path to desired x and y.
        
        Bresenham (straight line) by default.
        """
        return bresenham_path_to(self.entity.x, self.entity.y, x, y)


class WanderingAI(BaseAI):
    """AI that wanders the floors aimlessly"""
    CHANCE_TO_WALK: float = 0.75
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
        super().perform(engine)

        player_x = engine.player.x
        player_y = engine.player.y

        paths: list[tuple[int, int]] = self.get_path_to(player_x, player_y)

        self.update_agro_status(engine, paths)
        if self.agro:
            self.entity.add_component("ai", HostileEnemyAI(self.entity))
            return

        # Decide if creature wants to randomly walk to a tile.
        to_walk_or_not_to_walk_that_is_the_question: float = random.random()
        if to_walk_or_not_to_walk_that_is_the_question >= self.CHANCE_TO_WALK:
            # Pick a random, valid direction to walk to.
            dx, dy = random.choice(list(self.DIRECTIONS.values()))
            
            # Walk to that tile if it is not blocked by a blocking entity.
            BumpAction(self.owner, dx, dy).perform(engine)


class HostileEnemyAI(BaseAI):
    """AI that targets and fights the player; pseudo-pathfinding algorithm"""

    def perform(self, engine: Engine):
        super().perform(engine)

        floor: Floor = engine.dungeon.current_floor
        player_x = engine.player.x
        player_y = engine.player.y

        paths: list[tuple[int, int]] = self.get_path_to(
            floor, player_x, player_y)

        self.update_agro_status(engine, paths)
        if not self.agro:
            self.entity.add_component("ai", WanderingAI(self.entity))
            return

        next_path: tuple[int, int] = paths.pop(1)  # Second path is next path.

        desired_x, desired_y = next_path

        dx = desired_x - self.entity.x
        dy = desired_y - self.entity.y
        
        BumpAction(self.owner, dx, dy).perform(engine)
    
    def get_path_to(self, floor: Floor, x: int, y: int) -> list[tuple[int, int]]:
        return a_star_path_to(floor, self.entity.x, self.entity.y, x, y)

    
