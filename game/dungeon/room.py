from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .floor import Floor
    from ..engine import Engine
from ..tile import *

import random

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
           self.x1 <= room.x2
           and self.x2 >= room.x1
           and self.y1 <= room.y2
           and self.y2 >= room.y1
       )
    

    def get_random_cell(self) -> tuple[int, int]:
        """A random spot anywhere inside a room"""
        rand_x = random.randint(self.x1, self.x2 - 1)
        rand_y = random.randint(self.y1, self.y2 - 1)
        return rand_x, rand_y
    
    
    def explore(self, engine: Engine) -> None:
        """Explore and reveal room"""
        self.explored = True

        tiles: list[list[Tile]] = self.floor.tiles
        for x in range(self.x1 - 1, self.x2 + 1):
            for y in range(self.y1 - 1, self.y2 + 1):
                
                if tiles[x][y].char == WALL_TILE:
                    tiles[x][y] = wall_tile
                else:
                    tiles[x][y] = floor_tile
                
    
    