from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import Engine
    from ..entities import Entity
from ..actions import Action, BumpAction, WalkAction


class BaseComponent:
    """A basic component, lives in an entity's component pack"""
    owner: Entity


class BaseAI(Action, BaseComponent):
    """Basic AI that gets a path to a cell"""
    AGRO_RANGE: int = 8

    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.entity = entity
        self.agro = False


    def perform(self, engine: Engine):
        pass


    def update_agro_status(
            self, engine: Engine, paths: list[tuple[int, int]]) -> None:
        """
        Check each turn if enemy is in agro proximity to player and there is no
        boundary between them
        """
        player_x, player_y = engine.player.x, engine.player.y
        distance_from_player: float = self.distance_from(
            player_x, player_y
        )
        
        # Checking for blocked tiles in enemy paths.
        tiles = engine.dungeon.current_floor.tiles
        blocked: bool = any([not tiles[x][y].walkable for x,y in paths])

        if distance_from_player <= self.AGRO_RANGE and not blocked:
            self.agro = True
        else:
            self.agro = False

    
    def distance_from(self, x: int, y: int) -> float:
        """Distance formula"""
        return math.sqrt(
            (x - self.entity.x) ** 2 + (y - self.entity.y) ** 2
        )


    def get_path_to(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Get a set of coordinates from two points on the map following a
        straight line.
        
        Uses Bresenham's algorithm from RogueBasin:
        http://www.roguebasin.com/index.php/Bresenham%27s_Line_Algorithm#Python
        """
        # Setup initial conditions
        x1, y1 = (self.entity.x, self.entity.y)
        x2, y2 = (x, y)
        dx = x2 - x1
        dy = y2 - y1

        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)

        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        # Swap start and end points if necessary and store swap state
        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1

        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        # Iterate over bounding box generating points between start and end
        y = y1
        points = []
        for x in range(x1, x2 + 1):
            coord = (y, x) if is_steep else (x, y)
            points.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

        # Reverse the list if the coordinates were swapped
        if swapped:
            points.reverse()
        return points


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
        player_x = engine.player.x
        player_y = engine.player.y

        paths: list[tuple[int, int]] = self.get_path_to(player_x, player_y)

        self.update_agro_status(engine, paths)
        if self.agro:
            self.entity.add_component("ai", HostileEnemyAI(self.entity))
            return

        # Decide if creature wants to randomly walk to a tile.
        to_walk_or_not_to_walk_that_is_the_question: bool = random.random()
        if to_walk_or_not_to_walk_that_is_the_question >= self.CHANCE_TO_WALK:
            # Pick a random, valid direction to walk to.
            dx, dy = random.choice(list(self.DIRECTIONS.values()))
            
            # Walk to that tile if it is not blocked by a blocking entity.
            BumpAction(self.owner, dx, dy).perform(engine)


class HostileEnemyAI(BaseAI):
    """AI that targets and fights the playe; pseudo-pathfinding algorithm"""

    def perform(self, engine: Engine):
        player_x = engine.player.x
        player_y = engine.player.y

        paths: list[tuple[int, int]] = self.get_path_to(player_x, player_y)

        self.update_agro_status(engine, paths)
        if not self.agro:
            self.entity.add_component("ai", WanderingAI(self.entity))
            return

        next_path: tuple[int, int] = paths.pop(1)  # Second path is next path.

        desired_x, desired_y = next_path

        dx = desired_x - self.entity.x
        dy = desired_y - self.entity.y
        
        BumpAction(self.owner, dx, dy).perform(engine)

