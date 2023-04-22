from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Player
    from ..spawner import Spawner
from .floor import Floor, FloorBuilder


class Dungeon:
    """The dungeon composed of multiple floors the player must beat through"""
    
    def __init__(self,
                 spawner: Spawner,
                 num_floors: int,
                 max_enemies_per_floor: int,
                 max_items_per_floor: int,
                 floor_dimensions: tuple[int, int],
                 min_max_rooms: tuple[int, int],
                 min_max_room_width: tuple[int, int],
                 min_max_room_height: tuple[int, int]
                 ):
        self.spawner = spawner
        
        self.num_floors = num_floors
        self.max_enemies_per_floor = max_enemies_per_floor
        self.max_items_per_floor = max_items_per_floor
        self.floor_dimensions = floor_dimensions
        self.min_max_rooms = min_max_rooms
        self.min_max_room_width = min_max_room_width
        self.min_max_room_height = min_max_room_height

        self.floors: list[Floor] = []
        self.current_floor_idx: int = 0
    

    @property
    def current_floor(self) -> Floor:
        """Get the floor the player is currently on"""
        return self.floors[self.current_floor_idx]


    # TODO Increase difficulty per descending level.
    def generate(self) -> None:
        """Generate the the entirety of the dungeon"""

        # Regenerate if dungeon already exists.
        if self.floors:
            self.floors = []
            self.current_floor_idx = 0
        
        # Build the levels.
        for curr_idx in range(self.num_floors):
            num_rooms: int = random.randint(*(self.min_max_rooms))

            # Forming the rooms and connecting them.
            floor_builder: FloorBuilder = (
                FloorBuilder(self.floor_dimensions)
                    .place_walls()
                    .place_rooms(num_rooms,
                                 self.min_max_room_width,
                                 self.min_max_room_height)
                    .place_tunnels())
            
            # Figure out which staircases to put.
            descending, ascending = False, False
            if curr_idx < self.num_floors - 1:
                descending  = True
            if curr_idx > 0:
                ascending = True
            
            # Placing entities.
            # TODO randomize num_items and num_enemies.
            floor: Floor = (
                floor_builder
                    .place_staircases(self.spawner,
                                      descending,
                                      ascending)
                    .place_items(self.spawner, self.max_items_per_floor)
                    .place_creatures(self.spawner,
                                    self.max_enemies_per_floor)
                    .build(self))

            self.floors.append(floor)
    
    
    def spawn_player(self, player: Player) -> None:
        """Place a player in the first room upon entering a floor"""
        self.spawner.spawn_player(player, self.current_floor.first_room)

