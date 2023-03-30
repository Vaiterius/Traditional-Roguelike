from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Player
from .floor import Floor
from .room import Room
from .spawner import Spawner
from ..tile import *


class Dungeon:
    """The dungeon composed of multiple floors the player must beat through"""
    
    def __init__(self,
                 player: Player,
                 num_floors: int,
                 max_entities_per_room: int,
                 floor_dimensions: tuple[int, int],
                 min_max_rooms: tuple[int, int],
                 min_max_room_width: tuple[int, int],
                 min_max_room_height: tuple[int, int]
                 ):
        self.player = player

        self.num_floors = num_floors
        self.max_entities_per_room = max_entities_per_room
        self.floor_width, self.floor_height = floor_dimensions
        self.min_rooms, self.max_rooms = min_max_rooms
        self.min_room_width, self.max_room_width = min_max_room_width
        self.min_room_height, self.max_room_height = min_max_room_height

        self.floors: list[Floor] = []
        self.current_floor_idx: int = 0
        
        self.spawner = Spawner()
    

    @property
    def current_floor(self) -> Floor:
        return self.floors[self.current_floor_idx]


    # TODO Add dungeon level progression (inrcease difficulty).
    def generate(self) -> None:
        """Generate the the entirety of the dungeon"""

        # Regenerate if dungeon already exists.
        if self.floors:
            self.floors = []
            self.current_floor_idx = 0

        for curr_idx in range(self.num_floors):
            floor: Floor = self.generate_floor(curr_idx)
            self.floors.append(floor)
    

    def generate_floor(self, curr_idx: int) -> list[list[str]]:
        """Procedurally generate a floor for the next dungeon level"""
        # Starting 2D matrix of empty floors and walls.
        map_tiles = [
            [wall_tile_shrouded for x in range(self.floor_width)]
            for y in range(self.floor_height)
        ]

        # Create the actual floor object itself and add it to the dungeon.
        floor: Floor = Floor(
            width=self.floor_width,
            height=self.floor_height,
            dungeon=self,
            tiles=map_tiles,
            rooms=None,
            entities=[self.player]
        )
        floor.rooms = self.place_rooms(floor)
        
        # Add the staircases if applicable.
        self.spawner.spawn_staircases(
            floor, self.num_floors, curr_idx)

        return floor
    

    def spawn_player(self) -> None:
        """Place a player in the first room upon entering a floor"""
        self.spawner.spawn_player(self.player, self.current_floor.first_room)
    

    def place_rooms(self, floor: Floor) -> list[Room]:
        """Main procedural algorithm for placing tunnel-connected rooms"""
        map_tiles: list[list[Tile]] = floor.tiles

        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        rooms = []

        curr_iterations = 0
        while len(rooms) < num_rooms:
            room = Room(
                # Starting left x,y corner for room.
                x1 = random.randint(1, self.floor_height - self.max_room_height -1),
                y1 = random.randint(1, self.floor_width - self.max_room_width - 1),
                width=random.randint(self.min_room_width, self.max_room_width),
                height=random.randint(self.min_room_height, self.max_room_height),
                floor=floor
            )

            # We don't want rooms overlapping each other.
            if any(
                [room.intersects_with(placed_room) for placed_room in rooms]):
                # Too little space for another room check.
                curr_iterations += 1
                if curr_iterations > 250:
                    break  # Stop adding rooms.
                continue
            curr_iterations = 0
            
            # Start "digging" the room.
            for x in range(room.x1, room.x2):
                for y in range(room.y1, room.y2):
                    map_tiles[x][y] = floor_tile_shrouded
            
            # Place objects.
            # TODO

            # Place creatures.
            self.spawner.spawn_enemies_in_room(
                room,
                random.randint(0, self.max_entities_per_room)
            )
            
            rooms.append(room)

            if len(rooms) > 1:
                # Dig tunnel from this room to previous room.
                r1_cell = room.get_random_cell()
                r2_cell = rooms[-2].get_random_cell()

                for x, y in self.get_tunnel_set(r1_cell, r2_cell):
                    map_tiles[x][y] = floor_tile_shrouded
        
        return rooms



    def get_tunnel_set(
            self, r1_cell: tuple[int, int],
            r2_cell: tuple[int, int]
    ) -> set[tuple[int, int]]:
        tunnel_set = set()
        # First leg vertical, second leg horizontal.

        r1_cell_x, r1_cell_y = r1_cell
        r2_cell_x, r2_cell_y = r2_cell

        # Room 1 is above room 2.
        start_x = r1_cell_x
        end_x = r2_cell_x
        # Switch endpoints if room 1 is below room 2.
        if r1_cell_x >= r2_cell_x:
            start_x, end_x = end_x, start_x
        
        # Create x-axis coordinates, forming leg 1.
        for x in range(start_x, end_x + 1):
            if start_x == r1_cell_x:
                tunnel_set.add((x, r1_cell_y))
            else:
                tunnel_set.add((x, r2_cell_y))
        
        # Room 1 is to the left of room 2.
        start_y = r1_cell_y
        end_y = r2_cell_y
        # Switch endpoints if room 1 is below room 2.
        if r1_cell_y >= r2_cell_y:
            start_y, end_y = end_y, start_y
        
        # Create y-axis coordinates from end of leg 1.
        for y in range(start_y, end_y + 1):
            tunnel_set.add((end_x, y))
        
        return tunnel_set

