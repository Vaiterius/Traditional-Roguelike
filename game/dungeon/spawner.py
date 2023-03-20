from __future__ import annotations

import copy
import bisect
import random
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..entities import Player, Item
    from ..dungeon.room import Room
    from ..dungeon.floor import Floor
from ..render_order import RenderOrder
from ..entities import Creature, Entity
from ..config import enemies
from ..components.component import WanderingAI
from ..config import DESCENDING_STAIRCASE_TILE, ASCENDING_STAIRCASE_TILE

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
        self.ascending_staircase: Entity = copy.deepcopy(self.descending_staircase)
        self.ascending_staircase.name = "Ascending staircase"
        self.ascending_staircase.char = ASCENDING_STAIRCASE_TILE


    def add_to_sorted_entities(self,
        entities: list[Union[Player, Creature, Item]], entity: Entity) -> None:
        """Keep entities list sorted when adding"""
        bisect.insort(entities, entity, key=lambda x: x.render_order.value)
        
    
    def spawn_staircases(self,
        floor: Floor, num_floors: int, current_floor_idx: int) -> None:
        """To allow the player to descend the dungeon"""
        
        # Spawn descending staircase if there's a floor below.
        if current_floor_idx < num_floors - 1:
            rand_x, rand_y = floor.last_room.get_center_cell()
            descending_staircase = copy.deepcopy(self.descending_staircase)
            descending_staircase.x = rand_x
            descending_staircase.y = rand_y
            # Keep track of location.
            floor.descending_staircase_location = rand_x, rand_y
            self.add_to_sorted_entities(floor.entities, descending_staircase)

        # Spawn ascending staircase if there's a floor above.
        if current_floor_idx > 0:
            rand_x, rand_y = floor.first_room.get_center_cell()
            ascending_staircase = copy.deepcopy(self.ascending_staircase)
            ascending_staircase.x = rand_x
            ascending_staircase.y = rand_y
            # Keep track of location.
            floor.ascending_staircase_location = rand_x, rand_y
            self.add_to_sorted_entities(floor.entities, ascending_staircase)
    

    def spawn_player(self, player: Player, room: Room) -> None:
        rand_x, rand_y = room.get_center_cell()
        player.x, player.y =  rand_x, rand_y
    
    
    def spawn_enemies_in_room(self, room: Room, num_enemies: int) -> None:
        """Place creatures for the player to fight against"""
        for _ in range(num_enemies):
            rand_x, rand_y = room.get_random_empty_cell()
            
            enemy = self.get_random_enemy_instance()
            enemy.x, enemy.y = rand_x, rand_y
            
            self.add_to_sorted_entities(room.floor.entities, enemy)
    

    # TODO refactor dungeon and pass max_entities_per_room to method.
    def get_random_enemy_instance(self) -> object:
        """"""
        # Fetch a random enemy data object.
        enemy_data: dict = random.choices(
            population=list(enemies.values()),
            weights=[enemy["spawn_chance"] for enemy in enemies.values()]
        )[0]
        
        # Create the instance and spawn the enemy.
        enemy = Creature(
            x=-1,
            y=-1,
            name=enemy_data["name"],
            char=enemy_data["char"],
            color=enemy_data["color"],
            render_order=RenderOrder.CREATURE,
            hp=enemy_data["hp"],
            dmg=enemy_data["dmg"]
        )
        enemy.add_component("ai", WanderingAI(enemy))
        return enemy
    

    # TODO?? unnecessary maybe
    def spawn_random_enemy_instances(self) -> list[object]:
        pass