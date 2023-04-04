from __future__ import annotations

import copy
import bisect
import random
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .dungeon.room import Room
    from .dungeon.floor import Floor
from .render_order import RenderOrder
from .entities import Entity, Item, Creature, Player
from .data.creatures import player, enemies
from .components.component import HostileEnemyAI
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


    def add_to_sorted_entities(self,
        entities: list[Union[Player, Creature, Item]], entity: Entity) -> None:
        """Keep entities list sorted when adding for render order"""
        bisect.insort(entities, entity, key=lambda x: x.render_order.value)
    
    
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
        
        self.add_to_sorted_entities(floor.entities, staircase)
        
        return staircase
        
    
    def spawn_player(self, player: Player, room: Room) -> None:
        """Place the player in a selected room"""
        rand_x, rand_y = room.get_center_cell()  # On top of a staircase.
        player.x, player.y =  rand_x, rand_y
        self.add_to_sorted_entities(room.floor.entities, player)
    
    
    def spawn_enemy(self, room: Room) -> None:
        """Spawn a random creature and place it inside a room"""
        x, y = room.get_random_empty_cell()

        enemy: Creature = self._get_random_enemy_instance()
        enemy.x, enemy.y = x, y
        
        self.add_to_sorted_entities(room.floor.entities, enemy)
    
    
    def spawn_item(self, room: Room) -> None:
        """Spawn a random item and place it inside a room"""
        pass
    
    
    def get_player_instance(self) -> Player:
        """Load player data and create an instance out of it"""
        return Player(
            x=-1, y=-1,
            name=player["name"],
            char=player["char"],
            color=player["color"],
            render_order=RenderOrder.CREATURE,
            hp=player["hp"],
            mp=player["mp"],
            dmg=player["dmg"]
        )
    

    def _get_random_enemy_instance(self) -> Creature:
        """Load enemy data and create an instance out of it"""
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
            hp=enemy_data["hp"],
            dmg=enemy_data["dmg"],
            energy=enemy_data["energy"]
        )
        enemy.add_component("ai", HostileEnemyAI(enemy))
        return enemy
    
    
    def _get_random_item_instance(self) -> Item:
        """Load item data and create an instance out of it"""
        pass

