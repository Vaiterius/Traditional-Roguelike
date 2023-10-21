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
                 max_enemies_per_floor: int,
                 max_items_per_floor: int,
                 floor_dimensions: tuple[int, int],
                 min_max_rooms: tuple[int, int],
                 min_max_room_width: tuple[int, int],
                 min_max_room_height: tuple[int, int],
                 num_floors: int = -1,  # Endless mode default.
                 ):
        self.spawner = spawner
        
        self.max_enemies_per_floor = max_enemies_per_floor
        self.max_items_per_floor = max_items_per_floor
        self.floor_dimensions = floor_dimensions
        self.min_max_rooms = min_max_rooms
        self.min_max_room_width = min_max_room_width
        self.min_max_room_height = min_max_room_height
        self.num_floors = num_floors

        self.floors: list[Floor] = []
        self.current_floor_idx: int = 0
    

    @property
    def current_floor(self) -> Floor:
        """Get the floor the player is currently on"""
        return self.floors[self.current_floor_idx]
    
    @property
    def is_endless(self) -> bool:
        return self.num_floors == -1
    
    @property
    def is_last_floor(self) -> bool:
        """Only applies to normal mode"""
        return self.current_floor_idx == self.num_floors - 1
    
    @property
    def deepest_floor_idx(self) -> int:
        return len(self.floors) - 1
    

    def generate_floor(self) -> None:
        """Dynamically generate the next floor - used for endless modes"""
        num_rooms: int = random.randint(*(self.min_max_rooms))

        # Figure out which staircases to put.
        can_descend, can_ascend = True, False
        if self.current_floor_idx > 0:
            can_ascend = True
        if not self.is_endless:  # Normal mode.
            if self.is_last_floor:
                can_descend = False

        # TODO randomize num_items and num_enemies.
        # Forming the rooms and connecting them.
        floor: Floor = (
            FloorBuilder(self.floor_dimensions)
                .place_walls()
                .place_rooms(num_rooms,
                                self.min_max_room_width,
                                self.min_max_room_height)
                .place_tunnels()
                .place_staircases(self.spawner,
                                    can_descend,
                                    can_ascend)
                .place_items(self.spawner, self.max_items_per_floor)
                .place_creatures(self.spawner,
                                self.max_enemies_per_floor)
                .build(self)
        )
        
        self.floors.append(floor)


    # TODO Increase difficulty descending down levels (assign value?).
    def generate(self) -> None:
        """Prepare and generate the dungeon's first floor"""

        # Regenerate if dungeon already exists.
        if self.floors:
            self.floors = []
            self.current_floor_idx = 0

        self.generate_floor()
    
    
    def spawn_player(self, player: Player) -> None:
        """Place a player in the first room upon entering a floor"""
        self.spawner.spawn_player(player, self.current_floor.first_room)

