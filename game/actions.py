from __future__ import annotations

import sys
import bisect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from .engine import Engine
    from .entities import Creature, Entity
    from .save_handling import Save
from .tile import *
from .save_handling import (
    save_current_game,
    save_to_dir,
    delete_save_slot,
    fetch_saves
)


class Action:
    """Base action"""

    def __init__(self, entity: Entity):
        self.entity = entity

    def perform(self) -> None:
        """Overridable method"""
        pass


class QuitGameAction(Action):
    """Exit program"""

    def perform(self, engine: Engine):
        sys.exit(0)


class OnPlayerDeathAction(Action):
    """Delete save and return to main menu"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        delete_save_slot(engine.save)
        
        return turnable


class FromSavedataAction(Action):
    """Base action given save information"""
    
    def __init__(self, save: Save, saves_dir: Path, index: int) -> bool:
        self.save = save
        self.saves_dir = saves_dir
        self.index = index
    
    
    def _load_data_to_engine(self, engine: Engine, save: Save) -> None:
        """Loads a given save data into the engine"""
        engine.save = save
        engine.save_meta = save.metadata
        engine.player = save.data.get("player")
        engine.dungeon = save.data.get("dungeon")
        engine.message_log = save.data.get("message_log")


class DeleteSaveAction(FromSavedataAction):
    """Delete the selected save slot by index"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        # Delete save and refresh saves list.
        save: Save = fetch_saves(self.saves_dir)[self.index]
        delete_save_slot(save)
        engine.gamestate.saves = fetch_saves(self.saves_dir)
        
        return turnable


class SaveAndQuitAction(Action):
    """Saves the game before player quits"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        save_current_game(engine)
        
        return turnable


class StartNewGameAction(FromSavedataAction):
    """Start the dungeon crawling on the selected gamemode"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        save_to_dir(self.saves_dir, self.index, self.save)
        
        # TODO add game mode conditional
        self._load_data_to_engine(engine, self.save)
        
        engine.dungeon.generate()
        engine.dungeon.spawn_player(engine.player)
        engine.dungeon.current_floor.first_room.explore(engine)
        
        return turnable


class ContinueGameAction(FromSavedataAction):
    """Continue a previous save"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        self._load_data_to_engine(engine, self.save)

        engine.message_log.add(f"Welcome back, {engine.player.name}!")
        
        return turnable


class DoNothingAction(Action):
    """Do nothing this turn"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = True
        return turnable


class DescendStairsAction(Action):
    """Descend a flight of stairs to the next dungeon level"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        floor = engine.dungeon.current_floor

        player_x = engine.player.x
        player_y = engine.player.y
        
        # Ensure there exists a staircase to begin with.
        if floor.descending_staircase_location is None:
            return turnable
        
        # Player is standing on the staircase tile.
        staircase_x, staircase_y = floor.descending_staircase_location 
        if player_x == staircase_x and player_y == staircase_y:
            
            # Go down a level.
            engine.dungeon.current_floor_idx += 1
            room_to_spawn = engine.dungeon.current_floor.first_room
            engine.dungeon.spawner.spawn_player(
                engine.player, room_to_spawn)
            room_to_spawn.explore(self)
            
            engine.message_log.add(
                "You descend a level...")
        
        return turnable


class AscendStairsAction(Action):
    """Ascend a flight of stairs to the previous dungeon level"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        floor = engine.dungeon.current_floor

        player_x = engine.player.x
        player_y = engine.player.y
        
        # Ensure there exists a staircase to begin with.
        if floor.ascending_staircase_location is None:
            return turnable
        
        # Player is standing on the staircase tile.
        staircase_x, staircase_y = floor.ascending_staircase_location 
        if player_x == staircase_x and player_y == staircase_y:
            
            # Go up a level.
            engine.dungeon.current_floor_idx -= 1
            room_to_spawn = engine.dungeon.current_floor.last_room
            engine.dungeon.spawner.spawn_player(
                engine.player, room_to_spawn)
            room_to_spawn.explore(self)
            
            engine.message_log.add(
                "You ascend a level...")
        
        return turnable


class ExploreAction(Action):
    """Reveal the room and tunnels the player is in"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

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
                    
        return turnable


class ActionWithDirection(Action):
    """Base action with x,y directioning"""

    def __init__(self, entity: Creature, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy


class BumpAction(ActionWithDirection):
    """Action to decide what happens when a creature moves to a desired tile"""

    def perform(self, engine: Engine) -> bool:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        if floor.blocking_entity_at(desired_x, desired_y):
            return MeleeAction(self.entity, self.dx, self.dy).perform(engine)
        else:
            return WalkAction(self.entity, self.dx, self.dy).perform(engine)


class WalkAction(ActionWithDirection):
    """Action to validly move a creature"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        # TODO Get within bounds (turns out I don't need to do this?).
        # Get blocking tiles.
        if not floor.tiles[desired_x][desired_y].walkable:
            if self.entity == engine.player:
                engine.message_log.add(
                    "That way is blocked")
            return turnable
        # Get blocking entities.
        if floor.blocking_entity_at(desired_x, desired_y):
            return turnable
    
        turnable = True

        self.entity.move(dx=self.dx, dy=self.dy)
        
        # Explore environment around player.
        if self.entity == engine.player:
            ExploreAction(self.entity).perform(engine)
        
        return turnable


class MeleeAction(ActionWithDirection):
    """Action to hit a creature within melee range"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = True

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
            
            engine.message_log.add(
                f"{target.og_name} has perished!"
            )
            
            return turnable
        
        # Log info to message log.
        if target == engine.player:
            engine.message_log.add(
                f"{self.entity.name} hits you for {self.entity.dmg} points!",
                debug=True
            )
        elif self.entity == engine.player:
            engine.message_log.add(
                f"You hit {target.name} for {engine.player.dmg} points!",
                debug=True
            )
        else:
            engine.message_log.add(
                f"{self.entity.name} hits {target.name} for {self.entity.dmg} points! Lol!",
                debug=True
            )
        
        return turnable

