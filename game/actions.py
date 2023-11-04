from __future__ import annotations
from pathlib import Path

import sys
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pathlib import Path
    from .engine import Engine
    from .entities import Creature, Entity, Item
    from .save_handling import Save
    from .components.inventory import Inventory
    from .components.fighter import Fighter
    from .components.leveler import Leveler
    from .dungeon.floor import Floor
    from .components.equippable import Equippable
from .modes import GameMode
from .message_log import MessageType
from .tile import *
from .save_handling import (
    Save,
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


class ItemAction(Action):
    """Base item action for an entity performing something with it"""

    def __init__(self, entity: Entity, item: Item):
        super().__init__(entity)
        self.item = item


    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        if self.item.get_component("consumable") is not None:
            self.item.consumable.perform(engine)
        elif self.item.get_component("equippable") is not None:
            self.item.equippable.perform(engine)
        
        return turnable


class PickUpItemAction(Action):
    """Pick an item from off the floor and add it to inventory.
    
    It is not an `ItemAction` because we don't know if there's an item on the
    ground to be picked up at first - can't pass it to the constructor.
    """
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        inventory: Inventory = self.entity.inventory
        floor: Floor = engine.dungeon.current_floor
        item_to_pick_up: Optional[Item] = None
        
        # Check if an item actually exists at the carrier's location.
        for item in floor.items:
            if item.x == self.entity.x and item.y == self.entity.y:
                item_to_pick_up = item
                break
        
        # No item found underneath entity.
        if item_to_pick_up is None:
            engine.message_log.add("Nothing to be picked up here", color="red")
            return turnable

        # Not enough space in carrier's inventory.
        if inventory.size >= inventory.max_slots:
            if self.entity == engine.player:
                engine.message_log.add(
                    "There is not enough space in your inventory", color="red")
            return turnable
        
        # Pick up the item.
        floor.entities.remove(item)
        inventory.add_item(item)
        item.parent = self.entity

        # Check for quest item.
        # For now, this will be the main quest item found on the last floor
        # that the player needs to complete the game until we can get an actual
        # robust quest system in place.
        if item.get_component("quest_item") is not None:
            return item.quest_item.perform(engine)

        engine.message_log.add(
            f"You picked up: {item.name.lower()}", color="blue")

        return turnable
        

class DropItemAction(ItemAction):
    """Remove from inventory and drop an item onto the floor"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        inventory: Inventory = self.entity.inventory
        floor: Floor = engine.dungeon.current_floor
        
        # Unequip item if it is equipped.
        equippable: Equippable = self.item.get_component("equippable")
        if equippable and inventory.is_equipped(self.item):
            equippable.perform(engine)

        inventory.remove_item(self.item)
        self.item.place(floor, self.entity.x, self.entity.y)

        engine.message_log.add(
            f"You dropped: {self.item.name.lower()}", color="blue")
        
        return turnable


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

    def __init__(self,
                 save: Save,
                 saves_dir: Path,
                 index: int,
                 player_name: str = "Player") -> bool:
        super().__init__(save, saves_dir, index)
        self._player_name = player_name

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False

        # Set player name.
        self.save.data["player"].name = self._player_name
        if self.save.data["player"].name == "":
            self.save.data["player"].name = "Player"
        self.save.data["player"].og_name = self._player_name
        
        save_to_dir(self.saves_dir, self.index, self.save)
        
        assert engine.gamestate is not None
        self._load_data_to_engine(engine, self.save)
        
        # TODO create normal mode (story) and seeded mode
        if engine.save_meta["gamemode"] == GameMode.ENDLESS:
            engine.dungeon.generate()
            engine.dungeon.spawn_player(engine.player)
        elif engine.save_meta["gamemode"] == GameMode.NORMAL:
            engine.dungeon.generate()
            engine.dungeon.spawn_player(engine.player)
        
        save_current_game(engine)
        
        return turnable


class ContinueGameAction(FromSavedataAction):
    """Continue a previous save"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        self._load_data_to_engine(engine, self.save)

        engine.message_log.add(
            f"Welcome back, {engine.player.name}!", color="blue")
        
        return turnable


class LevelUpAction(Action):
    """Handle all logic for leveling up an entity"""

    def __init__(self, entity: Entity, attribute: Fighter.AttributeType):
        super().__init__(entity)
        self.attribute = attribute
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        
        leveler: Leveler = self.entity.leveler
        leveler.level_up()
        leveler.increment_attribute(self.attribute)

        engine.message_log.add(
            message=f"Leveled up to {leveler.level}",
            type=MessageType.INFO, color="green")

        return turnable


class DoNothingAction(Action):
    """Do nothing this turn"""

    def perform(self, engine: Engine) -> bool:
        from .gamestates import ExploreState  # Prevent circular import.
        turnable: bool = True

        if isinstance(engine.gamestate, ExploreState):
            engine.message_log.add("You take no action")
            engine.save_meta["turns"] += 1  # Record turn.

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
            engine.message_log.add("Can't descend here", color="red")
            return turnable
        
        # Check if player is standing on the staircase tile.
        staircase_x, staircase_y = floor.descending_staircase_location 
        if not (player_x == staircase_x and player_y == staircase_y):
            engine.message_log.add("Can't descend here", color="red")
            return turnable
            
        # Go down a level and generate new floor if needed.
        deepest_floor_idx = engine.dungeon.current_floor_idx
        if engine.dungeon.current_floor_idx == deepest_floor_idx:
            engine.dungeon.current_floor_idx += 1
            engine.dungeon.generate_floor()
        room_to_spawn = engine.dungeon.current_floor.first_room
        engine.dungeon.spawner.spawn_player(engine.player, room_to_spawn)
        
        engine.message_log.add(
            "You descend a level...", color="blue")
        
        engine.save_meta["turns"] += 1  # Record turn.
        
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
            engine.message_log.add("Can't ascend here", color="red")
            return turnable
        
        # Check if player is standing on the staircase tile.
        staircase_x, staircase_y = floor.ascending_staircase_location 
        if not (player_x == staircase_x and player_y == staircase_y):
            engine.message_log.add("Can't ascend here", color="red")
            return turnable
            
        # Go up a level.
        engine.dungeon.current_floor_idx -= 1
        room_to_spawn = engine.dungeon.current_floor.last_room
        engine.dungeon.spawner.spawn_player(
            engine.player, room_to_spawn)
        
        engine.message_log.add(
            "You ascend a level...", color="blue")
        
        engine.save_meta["turns"] += 1  # Record turn.
        
        return turnable


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

        # Get within bounds.
        if (
            (desired_x > floor.height - 1 or desired_x < 0)
            or (desired_y > floor.width - 1 or desired_y < 0)
        ):
            engine.message_log.add("Out of bounds", color="red")
            return turnable

        # Get blocking tiles.
        if not floor.tiles[desired_x][desired_y].walkable:
            if self.entity == engine.player:
                engine.message_log.add("That way is blocked", color="red")
            return turnable

        # Get blocking entities.
        if floor.blocking_entity_at(desired_x, desired_y):
            return turnable
    
        turnable = True

        self.entity.move(dx=self.dx, dy=self.dy)
        engine.save_meta["turns"] += 1  # Record turn.
        
        return turnable


class MeleeAction(ActionWithDirection):
    """Action to hit a creature within melee range"""

    def perform(self, engine: Engine) -> bool:
        turnable: bool = True

        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        # Prepare both parties and their respective combat components.
        initiator: Creature = self.entity
        initiator_fighter: Fighter = initiator.fighter
        initiator_leveler: Leveler = initiator.leveler

        target: Creature = floor.blocking_entity_at(desired_x, desired_y)
        target_fighter: Fighter = target.fighter
        target_leveler: Leveler = target.leveler
        
        target_slain_message: str = f"{target.og_name} has perished!"
        battle_message: str = ""
        message_type: MessageType = MessageType.INFO
        message_color: str = ""

        if initiator == engine.player:  # Record player.
            engine.save_meta["turns"] += 1

        # Chance to hit opponent fails.
        did_hit: bool = initiator_fighter.check_hit_success()
        if not did_hit:
            if target == engine.player:
                battle_message += f"{initiator.og_name} missed you"
                message_color = "blue"
                message_type = MessageType.ENEMY_ATTACK
            elif initiator == engine.player:
                battle_message += f"You missed {target.og_name}"
                message_color = "red"
                message_type = MessageType.PLAYER_ATTACK
            else:
                return turnable

            engine.message_log.add(
                message=battle_message, type=message_type, color=message_color)

            return turnable
        
        # Modify damage given/received based on opponents' stats.

        # Do it again if succeeds double hit check.
        did_double_hit: bool = initiator_fighter.check_double_hit_success()
        if did_double_hit:
            engine.message_log.add(
                "Double hit!", color=(
                    "green" if initiator == engine.player else "red"))
        for i in range(2 if did_double_hit else 1):
            # Critical hit check.
            did_critical: bool = initiator_fighter.check_critical_hit_success()
            damage_given: int = 0
            if did_critical:
                damage_given = initiator_fighter.critical_damage
            else:
                damage_given = initiator_fighter.damage
            target_fighter.take_damage(damage_given)
            
            # Log hit success.
            if target == engine.player:
                battle_message = f"{initiator.og_name} hits you for " \
                                 f"{damage_given} pts"
                message_type = MessageType.ENEMY_ATTACK
                message_color = "red"
            elif initiator == engine.player:
                battle_message = f"You hit {target.og_name} for " \
                                 f"{damage_given} pts"
                message_type = MessageType.PLAYER_ATTACK
                message_color="blue"
            else:
                return turnable

            battle_message += " !!!" if did_critical else ""
            
            engine.message_log.add(
                message=battle_message, type=message_type, color=message_color)
        
        # TODO add check for player or enemy knockout.

        # Target opponent has been slain.
        if target_fighter.is_dead:
            experience_drop: int = target.leveler.experience_drop
            floor.entities.remove(target)
            floor.add_entity(target)
            engine.message_log.add(target_slain_message)

            if initiator == engine.player:
                engine.save_meta["slayed"] += 1
                engine.message_log.add(
                    message=f"You slayed {target.og_name} " \
                            f"and gained {experience_drop} EXP!",
                    type=MessageType.INFO, color="green")

            # Absorb experience.
            initiator_leveler.absorb(
                incoming_experience=target_leveler.experience_drop)
        
        return turnable

