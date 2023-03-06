import random
from typing import Any

from tile import Tile
from entities import Player, Creature


class Room:

    def __init__(self, x1: int, y1: int, width: int, height: int):
        self.x1 = x1
        self.y1 = y1

        # Inverted because x-axis going down is our height.
        self.x2 = x1 + height
        self.y2 = y1 + width

        self.width = width
        self.height = height
    

    def intersects_with(self, room: "Room") -> bool:
        return (
           self.x1 <= room.x2
           and self.x2 >= room.x1
           and self.y1 <= room.y2
           and self.y2 >= room.y1
       )
    

    def get_random_cell(self) -> tuple[int]:
        rand_x = random.randint(self.x1, self.x2)
        rand_y = random.randint(self.y1, self.y2)
        return rand_x, rand_y


class Floor:

    def __init__(self,
                 width: int,
                 height: int,
                 dungeon: "Dungeon",
                 tiles: list[list[Tile]],
                 rooms: list[Room],
                 entities: list[Player|Creature],
                 objects: list[Any]):
        self.width = width
        self.height = height

        self.dungeon = dungeon

        self.tiles = tiles

        self.rooms = rooms

        self.entities = entities
        self.objects = objects
    
    
    @property
    def first_room(self) -> Room:
        return self.rooms[0]


class Dungeon:
    
    def __init__(self,
                 player: Player,
                 wall_char: str,
                 floor_char: str,
                 num_floors: int,
                 floor_dimensions: tuple[int],
                 min_max_rooms: tuple[int],
                 min_max_room_width: tuple[int],
                 min_max_room_height: tuple[int]
                 ):
        self.player = player

        self.wall_tile = Tile(char=wall_char, walkable=False)
        self.floor_tile = Tile(char=floor_char, walkable=True)

        self.num_floors = num_floors
        self.floor_width, self.floor_height = floor_dimensions
        self.min_rooms, self.max_rooms = min_max_rooms
        self.min_room_width, self.max_room_width = min_max_room_width
        self.min_room_height, self.max_room_height = min_max_room_height

        self.floors: list[Floor] = []
        self.current_floor_idx: int = 0
    

    @property
    def current_floor(self):
        return self.floors[self.current_floor_idx]
    

    def generate_floor(self) -> list[list[str]]:
        map_tiles = [
            [self.wall_tile for x in range(self.floor_width)]
            for y in range(self.floor_height)
        ]
        rooms: list[Room] = self.place_rooms(map_tiles)
        floor: Floor = Floor(
            width=self.floor_width,
            height=self.floor_height,
            dungeon=self,
            tiles=map_tiles,
            rooms=rooms,
            entities=[],
            objects=[]
        )
        self.floors.append(floor)
    

    def spawn_player(self) -> None:
        first_room: Room = self.current_floor.first_room
        spawn_x, spawn_y = first_room.get_random_cell()
        self.player.x, self.player.y = spawn_x, spawn_y
    

    def place_rooms(self, map_tiles: list[list[str]]) -> list[Room]:
        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        rooms = []

        curr_iterations = 0
        while len(rooms) < num_rooms:
            room = Room(
                # Starting left x,y corner for room.
                x1 = random.randint(0, self.floor_height - self.max_room_height - 1),
                y1 = random.randint(0, self.floor_width - self.max_room_width - 1),
                width=random.randint(self.min_room_width, self.max_room_width),
                height=random.randint(self.min_room_height, self.max_room_height)
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
            for x in range(room.x1, room.x2 + 1):
                for y in range(room.y1, room.y2 + 1):
                    map_tiles[x][y] = self.floor_tile
            
            rooms.append(room)

            if len(rooms) > 1:
                # Dig tunnel from this room to previous room.
                r1_cell = room.get_random_cell()
                r2_cell = rooms[-2].get_random_cell()

                for x, y in self.get_tunnel_set(r1_cell, r2_cell):
                    map_tiles[x][y] = self.floor_tile
        
        return rooms



    def get_tunnel_set(
            self, r1_cell: tuple[int], r2_cell: tuple[int]) -> set[tuple]:
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

