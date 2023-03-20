from __future__ import annotations

import bisect
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


class DescendStairsAction(Action):
    """Descend a flight of stairs to the next dungeon level"""
    
    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        player_x = engine.player.x
        player_y = engine.player.y
        
        # Ensure there exists a staircase to begin with.
        if floor.descending_staircase_location is None:
            return
        
        # Player is standing on the staircase tile.
        staircase_x, staircase_y = floor.descending_staircase_location 
        if player_x == staircase_x and player_y == staircase_y:
            
            # Go down a level.
            engine.dungeon.current_floor_idx += 1
            room_to_spawn = engine.dungeon.current_floor.first_room
            engine.dungeon.spawner.spawn_player(
                engine.player, room_to_spawn)
            room_to_spawn.explore(self)
            
            engine.terminal_controller.message_log.add(
                "You descend a level...")


class AscendStairsAction(Action):
    """Ascend a flight of stairs to the previous dungeon level"""
    
    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        player_x = engine.player.x
        player_y = engine.player.y
        
        # Ensure there exists a staircase to begin with.
        if floor.ascending_staircase_location is None:
            return
        
        # Player is standing on the staircase tile.
        staircase_x, staircase_y = floor.ascending_staircase_location 
        if player_x == staircase_x and player_y == staircase_y:
            
            # Go up a level.
            engine.dungeon.current_floor_idx -= 1
            room_to_spawn = engine.dungeon.current_floor.last_room
            engine.dungeon.spawner.spawn_player(
                engine.player, room_to_spawn)
            room_to_spawn.explore(self)
            
            engine.terminal_controller.message_log.add(
                "You ascend a level...")


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
            # Change sorted render order position.
            floor.entities.remove(target)
            bisect.insort(
                floor.entities, target, key=lambda x: x.render_order.value)
            
            engine.terminal_controller.message_log.add(
                f"{target.og_name} has perished!",
                debug=True
            )
            return
        
        # Log info to message log.
        if target == engine.player:
            engine.terminal_controller.message_log.add(
                f"{self.entity.name} hits you for {self.entity.dmg} points!",
                debug=True
            )
        elif self.entity == engine.player:
            engine.terminal_controller.message_log.add(
                f"You hit {target.name} for {engine.player.dmg} points!",
                debug=True
            )
        else:
            engine.terminal_controller.message_log.add(
                f"{self.entity.name} hits {target.name} for {self.entity.dmg} points! Lol!",
                debug=True
            )

