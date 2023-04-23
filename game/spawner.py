from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon.room import Room
    from .dungeon.floor import Floor
from .components.inventory import Inventory
from .components.fighter import Fighter
from .render_order import RenderOrder
from .entities import Entity, Item, Creature, Player
from .data.creatures import enemies, player
from .data.items.potions import restoration_potions
from .data.items.armor import armor
from .data.config import DESCENDING_STAIRCASE_TILE, ASCENDING_STAIRCASE_TILE

class Spawner:
    """Helper object for spawning entities in the dungeon"""
    
    def __init__(self):
        # Create staircase prefabs.
        self.descending_staircase: Entity = Entity(
            x=-1, y=-1,
            name="Descending staircase",
            char=DESCENDING_STAIRCASE_TILE,
            color="white",
            render_order=RenderOrder.STAIRCASE,
            blocking=False
        )
        self.ascending_staircase: Entity = copy.deepcopy(
            self.descending_staircase)
        self.ascending_staircase.name = "Ascending staircase"
        self.ascending_staircase.char = ASCENDING_STAIRCASE_TILE


    def spawn_staircase(
        self, floor: Floor, x: int, y: int, type: str) -> Entity:
        """Place a descending or ascending staircase somewhere in the level"""
        staircase: Entity = None
        
        if type == "descending":
            staircase = self.descending_staircase.spawn_clone()
            floor.descending_staircase_location = x, y
        elif type == "ascending":
            staircase = self.ascending_staircase.spawn_clone()
            floor.ascending_staircase_location = x, y
        
        staircase.x = x
        staircase.y = y
        
        floor.add_entity(staircase)
        
        return staircase
        
    
    def spawn_player(self, player: Player, room: Room) -> None:
        """Place the player in a selected room"""
        x, y = room.get_center_cell()  # On top of a staircase.
        player.x, player.y =  x, y
        room.floor.add_entity(player)
    
    
    def spawn_enemy(self, room: Room) -> None:
        """Spawn a random creature and place it inside a room"""
        x, y = room.get_random_empty_cell()

        enemy: Creature = self._get_random_enemy_instance()
        enemy.x, enemy.y = x, y
        
        room.floor.add_entity(enemy)
    
    
    def spawn_item(self, room: Room) -> None:
        """Spawn a random item and place it inside a room"""
        x, y = room.get_random_empty_cell()
        
        item: Item = self._get_random_item_instance()
        item.x, item.y = x, y
        
        room.floor.add_entity(item)
    
    
    def get_player_instance(self) -> Player:
        """Load player data and create an instance out of it"""
        player_obj = Player(
            x=-1, y=-1,
            name=player["name"],
            char=player["char"],
            color=player["color"],
            render_order=RenderOrder.CREATURE,
        )
        player_obj.add_component(
            name="fighter",
            component=Fighter(
                health=player["hp"],
                magicka=player["mp"],
                base_damage=player["dmg"],
                base_agility=-1,
                base_power=-1,
                base_sage=-1,
                base_vitality=-1
            )
        )
        player_obj.add_component("inventory", Inventory(num_slots=16))
        # TODO remove test items
        test_item_1 = Item(-1, -1, "test_item_1", "`", "default", RenderOrder.ITEM, False)
        test_item_2 = Item(-1, -1, "test_item_2", "`", "default", RenderOrder.ITEM, False)
        test_item_3 = Item(-1, -1, "test_item_3", "`", "default", RenderOrder.ITEM, False)
        player_obj.inventory.add_items([test_item_1, test_item_2, test_item_3])
        
        return player_obj


    def _get_random_enemy_instance(self) -> Creature:
        """Load enemy data and create an instance out of it"""
        # Prevent circular import.
        from .components.ai import HostileEnemyAI

        # Fetch a random enemy data object.
        enemy_data: dict = random.choices(
            population=list(enemies.values()),
            weights=[enemy["spawn_chance"] for enemy in enemies.values()]
        )[0]
        
        # Create the instance and spawn the enemy.
        enemy = Creature(
            x=-1, y=-1,
            name=enemy_data["name"],
            char=enemy_data["char"],
            color=enemy_data["color"],
            render_order=RenderOrder.CREATURE,
            energy=enemy_data["energy"]
        )
        enemy.add_component(
            name="fighter",
            component=Fighter(
                health=enemy_data["hp"],
                magicka=-1,
                base_damage=enemy_data["dmg"],
                base_agility=-1,
                base_power=-1,
                base_sage=-1,
                base_vitality=-1
            )
        )
        enemy.add_component("ai", HostileEnemyAI(enemy))
        return enemy
    
    
    # TODO for now, this will only spawn health/magicka potions
    def _get_random_item_instance(self) -> Item:
        """Load item data and create an instance out of it"""
        # Prevent circular import.
        from .components.consumable import (
            RestoreHealthConsumable, RestoreMagickaConsumable)
        
        # Fetch a random potion data object.
        potion_data: dict = random.choices(
            population=list(restoration_potions.values()),
            weights=[
                potion["spawn_chance"]
                for potion in restoration_potions.values()]
        )[0]
        
        # Create the instance and spawn the item.
        potion = Item(
            x=-1, y=-1,
            name=potion_data["name"],
            char=potion_data["char"],
            color=potion_data["color"],
            render_order=RenderOrder.ITEM,
            blocking=False
        )
        name: str = potion_data["name"]
        if name == "Potion of Restore Health":
            potion.add_component(
                "consumable", RestoreHealthConsumable(potion_data["yield"]))
        elif name == "Potion of Restore Magicka":
            potion.add_component(
                "consumable", RestoreMagickaConsumable(potion_data["yield"]))
        
        return potion

