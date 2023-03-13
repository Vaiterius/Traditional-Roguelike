from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .entities import Creature, Entity
from .tile import *


class Action:
    """Base action"""

    def __init__(self, entity: Entity):
        self.entity = entity

    def perform(self) -> None:
        """Overridable method"""
        pass


class WaitAction(Action):
    """Do nothing this turn"""

    def perform(self, engine: Engine) -> None:
        pass


class ExploreAction(Action):
    """Reveal the room and tunnels the player is in"""
    
    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        player_x = engine.player.x
        player_y = engine.player.y

        # Reveal room.
        for room in floor.unexplored_rooms:
            if (
                player_x >= room.x1
                and player_x <= room.x2
                and player_y >= room.y1
                and player_y <= room.y2
            ):
                room.explore(engine)
        
        # Reveal one surrounding tile distance of tunnel.
        tiles = floor.tiles
        for x in range(player_x - 1, player_x + 2):
            for y in range(player_y - 1, player_y + 2):
                if tiles[x][y].char == WALL_TILE:
                    tiles[x][y] = wall_tile
                else:
                    tiles[x][y] = floor_tile


class ActionWithDirection(Action):
    """Base action with x,y directioning"""

    def __init__(self, entity: Creature, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy


class BumpAction(ActionWithDirection):
    """Action to decide what happens when a creature moves to a desired tile"""

    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        if floor.blocking_entity_at(desired_x, desired_y):
            MeleeAction(self.entity, self.dx, self.dy).perform(engine)
        else:
            WalkAction(self.entity, self.dx, self.dy).perform(engine)


class WalkAction(ActionWithDirection):
    """Action to validly move a creature"""

    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        # Get within bounds.
        # TODO
        # Get blocking tiles.
        if not floor.tiles[desired_x][desired_y].walkable:
            if self.entity == engine.player:
                engine.terminal_controller.message_log.add(
                    "That way is blocked")
            return
        # Get blocking entities.
        if floor.blocking_entity_at(desired_x, desired_y):
            return

        self.entity.move(dx=self.dx, dy=self.dy)
        
        # Explore environment around player.
        if self.entity == engine.player:
            ExploreAction(self.entity).perform(engine)


class MeleeAction(ActionWithDirection):
    """Action to hit a creature within melee range"""

    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        target: Entity = floor.blocking_entity_at(desired_x, desired_y)
        target.set_hp(target.hp - self.entity.dmg)
        
        if target.is_dead:
            engine.terminal_controller.message_log.add(
                f"{target.og_name} has perished!",
                True
            )
            return
        
        # Log info to message log.
        if target == engine.player:
            engine.terminal_controller.message_log.add(
                f"{self.entity.name} hits you for {self.entity.dmg} points!",
                True
            )
        elif self.entity == engine.player:
            engine.terminal_controller.message_log.add(
                f"You hit {target.name} for {engine.player.dmg} points!",
                True
            )
        else:
            engine.terminal_controller.message_log.add(
                f"{self.entity.name} hits {target.name} for {self.entity.dmg} points! Lol!",
                True
            )

