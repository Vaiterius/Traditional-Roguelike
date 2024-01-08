from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

from game.engine import Engine

if TYPE_CHECKING:
    from ..engine import Engine
    from ..entities import Entity
    from .leveler import Leveler
    from ..dungeon.floor import Floor
    from ..dungeon.room import Room
from .fighter import Fighter
from .base_component import BaseComponent
from ..actions import Action, BumpAction
from ..pathfinding import bresenham_path_to, a_star_path_to
from ..data.config import CHANCE_TO_SWITCH_ROOMS, CHANCE_TO_TAKE_STEP


class BaseAI(Action, BaseComponent):
    """Basic AI that gets a path to a cell"""
    AGRO_RANGE: int = 8

    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.entity = entity
        self.agro = False


    def perform(self, engine: Engine) -> None:
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


### ENEMY AI ###


class WanderingAI(BaseAI):
    """AI that wanders the floor of the dungeon"""
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

    def player_in_sight(self, engine: Engine) -> bool:
        """
        See if the entity senses where the player is given a straight line
        """
        line_to_player: list[tuple[int, int]] = bresenham_path_to(
            self.entity.x, self.entity.y, engine.player.x, engine.player.y)
        self.update_agro_status(engine, line_to_player)
        if self.agro:
            return True
        return False


class WanderingToRoomAI(WanderingAI):
    """Wandering AI that is currently travelling to another room"""

    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._target_room_cell: Optional[tuple[int, int]] = None
        self._current_path_to_room: list[tuple[int, int]] = []
    
    def perform(self, engine: Engine) -> None:
        super().perform(engine)
        floor: Floor = engine.dungeon.current_floor

        if self.player_in_sight(engine):
            self.entity.add_component("ai", HostileEnemyAI(self.entity))
            return
        
        # Pick random spot in the room to travel to and set paths.
        if not self._target_room_cell or self._current_path_to_room == []:
            room: Room = engine.rng.choice(floor.rooms)
            self._target_room_cell = room.get_random_cell()

            self._current_path_to_room = a_star_path_to(
            floor, self.entity.x, self.entity.y, *self._target_room_cell)
        
        # Chance to switch over to pacing around the current room if already
        # reached desired room.
        if engine.rng.random() <= CHANCE_TO_SWITCH_ROOMS:
            self.entity.add_component("ai", WanderingAroundRoomAI(self.entity))
            return
        
        # Continue the path towards the desired room.
        if self._current_path_to_room != []:
            next_path: tuple[int, int] = self._current_path_to_room.pop(0)

            desired_x, desired_y = next_path

            dx = desired_x - self.entity.x
            dy = desired_y - self.entity.y
            
            BumpAction(self.owner, dx, dy, no_hit=True).perform(engine)
            return
        
        # Has already reached target room/cell.
        self.entity.add_component("ai", WanderingAroundRoomAI(self.entity))


class WanderingAroundRoomAI(WanderingAI):
    """Wandering AI that is currently pacing around a room"""

    def perform(self, engine: Engine) -> None:
        super().perform(engine)

        if self.player_in_sight(engine):
            self.entity.add_component("ai", HostileEnemyAI(self.entity))
            return
        
        # Chance to switch over to wandering to a different room.
        if engine.rng.random() <= CHANCE_TO_SWITCH_ROOMS:
            self.entity.add_component("ai", WanderingToRoomAI(self.entity))
            return
        
        # Pace around the room.

        # AI can stay in place or take random steps around.
        if engine.rng.random() >= CHANCE_TO_TAKE_STEP:
            return
        
        # Pick a random direction to walk to.
        dx, dy = engine.rng.choice(list(self.DIRECTIONS.values()))
        BumpAction(self.owner, dx, dy, no_hit=True).perform(engine)


class HostileEnemyAI(BaseAI):
    """AI that chases and fights the player"""

    def perform(self, engine: Engine) -> None:
        super().perform(engine)

        floor: Floor = engine.dungeon.current_floor
        player_x = engine.player.x
        player_y = engine.player.y

        paths: list[tuple[int, int]] = a_star_path_to(
            floor, self.entity.x, self.entity.y, player_x, player_y)

        self.update_agro_status(engine, paths)
        if not self.agro:
            self.entity.add_component("ai", WanderingAroundRoomAI(self.entity))
            return

        # Go down the path towards the player.
        if paths != []:
            next_path: tuple[int, int] = paths.pop(0)

            desired_x, desired_y = next_path

            dx = desired_x - self.entity.x
            dy = desired_y - self.entity.y
            
            BumpAction(self.owner, dx, dy).perform(engine)
            return
        
        # Can't get to player, maybe other entities completely blocking them,
        # so just stand around.


# TODO make AI where enemy flees from player when close to death.
class FleeingAI(WanderingAI):
    pass
        

### TEMPORARY EFFECTS AI ###


class EffectPerTurnAI(BaseAI):
    """AI that lasts for a given number of turns"""

    def __init__(
            self, entity: Entity, previous_ai: BaseAI, turns_remaining: int):
        super().__init__(entity)
        self._previous_ai = previous_ai
        self._turns_remaining = turns_remaining


class ConfusedAI(WanderingAI, EffectPerTurnAI):
    """AI that confusedly bumps into every direction, aimlessly"""
    
    def perform(self, engine: Engine) -> None:
        super().perform(engine)

        # Confusion effect has worn off.
        if self._turns_remaining <= 0:
            engine.message_log.add(f"{self.entity.name} is no longer confused")
            self.entity.add_component("ai", self._previous_ai)
            return
        
        # Pick a random direction to walk to.
        dx, dy = engine.rng.choice(list(self.DIRECTIONS.values()))
        BumpAction(self.owner, dx, dy, no_hit=False).perform(engine)

        self._turns_remaining -= 1


class FrozenAI(EffectPerTurnAI):
    """AI that stays in its place for a given amount of time"""

    def perform(self, engine: Engine) -> None:
        super().perform(engine)

        # Frozen effect has worn off.
        if self._turns_remaining <= 0:
            engine.message_log.add(f"{self.entity.name} is no longer frozen")
            self.entity.add_component("ai", self._previous_ai)
            return
        
        # Do absolutely nothing.
        
        self._turns_remaining -= 1

