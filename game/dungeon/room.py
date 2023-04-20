from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .floor import Floor
    from ..engine import Engine
from ..tile import *

class Room:
    """Rectangular rooms found on each floor"""

    def __init__(self,
                 x1: int,
                 y1: int,
                 width: int,
                 height: int,
                 floor: Floor):
        self.x1 = x1
        self.y1 = y1

        # Inverted because x-axis going down is our height.
        self.x2 = x1 + height
        self.y2 = y1 + width

        self.width = width
        self.height = height

        self.floor = floor
        self.explored = False
    

    def intersects_with(self, room: Room) -> bool:
        """Check if this room is overlapping with another room"""
        return (
           self.x1 <= room.x2 + 1
           and self.x2 >= room.x1 - 1
           and self.y1 <= room.y2 + 1
           and self.y2 >= room.y1 - 1
       )

    
    def get_center_cell(self) -> tuple[int, int]:
        """The spot in the middle of the room"""
        center_x = (self.x1 + ((self.x2 - self.x1) // 2))
        center_y = (self.y1 + ((self.y2 - self.y1) // 2))
        return center_x, center_y
    

    def get_random_cell(self) -> tuple[int, int]:
        """A random spot anywhere inside a room"""
        rand_x = random.randint(self.x1, self.x2 - 1)
        rand_y = random.randint(self.y1, self.y2 - 1)
        return rand_x, rand_y

    
    def get_random_empty_cell(self) -> tuple[int, int]:
        """A random spot that's not occupied by a blocking entity"""
        rand_x, rand_y = self.get_random_cell()
        while self.floor.blocking_entity_at(rand_x, rand_y) is not None:
            rand_x, rand_y = self.get_random_cell()
        return rand_x, rand_y
    
    