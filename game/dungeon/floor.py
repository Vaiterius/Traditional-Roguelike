from __future__ import annotations

import bisect
from typing import Iterator, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon import Dungeon
    from ..entities import Entity, Player
    from ..tile import Tile
    from ..spawner import Spawner
    from ..rng import RandomNumberGenerator
from .room import Room
from ..entities import Creature, Item, Player
from ..tile import *


class Floor:
    """A dungeon floor of rooms filled with objects, entities, and you"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.tiles: list[list[Tile]] = []
        self.wall_locations: set[tuple[int, int]] = set()  # For A* algorithm.
        self.explored_tiles: dict[tuple[int, int], Tile] = {}
        
        self.rooms: list[Room] = []
        self.entities: list[Union[Player, Creature, Item]] = []
        
        self.dungeon: Optional[Dungeon] = None

        self.descending_staircase_location: tuple[int, int] = None
        self.ascending_staircase_location: tuple[int, int] = None
    
    
    @property
    def items(self) -> Iterator[Item]:
        """Select the items from the entities list"""
        yield from (
            entity for entity in self.entities
            if isinstance(entity, Item)
        )
    
    
    @property
    def creatures(self) -> Iterator[Creature]:
        """Select the creatures from the entities list"""
        yield from (
            entity for entity in self.entities
            if isinstance(entity, Creature)
        )
    
    
    @property
    def unexplored_rooms(self) -> Iterator[Room]:
        """Select the rooms already explored from the player"""
        yield from (room for room in self.rooms if not room.explored)
    
    
    @property
    def first_room(self) -> Room:
        """Get the room that was first created"""
        return self.rooms[0]
    
    
    @property
    def last_room(self) -> Room:
        """Get the room that was last created"""
        return self.rooms[-1]
    
    
    def get_random_room(self, rng: RandomNumberGenerator) -> Room:
        """Get a random room"""
        return rng.choice(self.rooms)
    
    
    def blocking_entity_at(
        self,
        x: int,
        y: int,
        include_player: bool = True
    ) -> Optional[Union[Player, Creature]]:
        """Check if a cell is occupied by an entity that blocks movement"""
        for entity in self.entities:
            if isinstance(entity, Player) and not include_player:
                continue
            if entity.x == x and entity.y == y and entity.blocking:
                return entity
        return None
    
    
    def add_entity(self, entity: Entity) -> None:
        """Keep entities list sorted when adding by render order"""
        bisect.insort(
            self.entities, entity, key=lambda x: x.render_order.value)


class FloorBuilder:
    """Methods to build and customize dungeon levels step-by-step"""
    
    def __init__(
        self,
        rng: RandomNumberGenerator,
        floor_height: int,
        floor_width: int
    ):
        self.rng = rng
        self.floor_height = floor_height
        self.floor_width = floor_width

        self._floor = Floor(
            width=self.floor_width,
            height=self.floor_height
        )
    
    
    def place_walls(
        self, tile_type: Tile = wall_tile_shrouded) -> FloorBuilder:
        """Fill the floor with wall tiles"""
        for x in range(self.floor_height):
            row: list[Tile] = []
            for y in range(self.floor_width):
                row.append(tile_type)
                # Track for pathfinding.
                self._floor.wall_locations.add((x, y))
            self._floor.tiles.append(row)
        return self
    
    
    # TODO add prefab rooms
    
    
    def place_rooms(
        self,
        num_rooms: int,
        min_room_height: int,
        max_room_height: int,
        min_room_width: int,
        max_room_width: int,
        tile_type: Tile = floor_tile_shrouded
    ) -> FloorBuilder:
        """Algorithm to scatter randomly-sized rooms across the floor"""
        # Place rooms until we reach our desired limit.
        curr_iterations = 0
        while len(self._floor.rooms) < num_rooms:
            room = Room(
                rng=self.rng,
                # Starting left x,y corner for room.
                x1 = self.rng.randint(1, self.floor_height - max_room_height -1),
                y1 = self.rng.randint(1, self.floor_width - max_room_width - 1),
                width=self.rng.randint(min_room_width, max_room_width),
                height=self.rng.randint(min_room_height, max_room_height),
                floor=self._floor
            )
            
            # We don't want rooms overlapping each other.
            if any(
                [
                    room.intersects_with(placed_room)
                    for placed_room in self._floor.rooms
                ]
            ):
                # Too little space for another room check.
                curr_iterations += 1
                if curr_iterations > 250:
                    break  # Stop adding rooms.
                continue
            curr_iterations = 0
            
            # Start "digging" the room.
            for x in range(room.x1, room.x2):
                for y in range(room.y1, room.y2):
                    self._floor.tiles[x][y] = tile_type
                    # Track for pathfinding.
                    self._floor.wall_locations.remove((x, y))
            
            self._floor.rooms.append(room)
        
        return self
    
    
    def place_tunnels(self, tile_type: Tile = floor_tile_dim) -> FloorBuilder:
        """Build a tunnel path from one room to the next"""
        rooms: list[Room] = self._floor.rooms
        for room in rooms:
            if len(rooms) > 1:
                # Dig tunnel from this room to previous room.
                r1_cell = room.get_random_cell()
                r2_cell = rooms[-2].get_random_cell()

                for x, y in self._get_tunnel_set(r1_cell, r2_cell):
                    self._floor.tiles[x][y] = tile_type
                    # Track for pathfinding.
                    self._floor.wall_locations -= {(x, y)}
        
        return self
    
    
    def place_staircases(
        self,
        spawner: Spawner,
        descending: bool,
        ascending: bool
    ) -> FloorBuilder:
        """Create and place the descending/ascending staircases"""
        if descending:
            x, y = self._floor.last_room.get_center_cell()
            spawner.spawn_staircase(self._floor, x, y, "descending")

        if ascending:
            x, y = self._floor.first_room.get_center_cell()
            spawner.spawn_staircase(self._floor, x, y, "ascending")

        return self
    
    
    def place_items(
        self,
        spawner: Spawner,
        max_items_per_floor: int
    ) -> FloorBuilder:
        """Scatter random items throughout the level"""
        for _ in range(max_items_per_floor):
            room: Room = self.rng.choice(self._floor.rooms)
            spawner.spawn_item(room, item_type="normal")
        
        return self
    
    
    def place_creatures(
        self, 
        spawner: Spawner, 
        max_creatures_per_floor: int
    ) -> FloorBuilder:
        """Create and place enemies throughout the rooms in the level"""
        for _ in range(max_creatures_per_floor):
            # Don't include the room the player spawns in.
            room: Room = self.rng.choice(self._floor.rooms[1:])
            spawner.spawn_enemy(room)
        
        return self
    
    
    def build(self, dungeon: Optional[Dungeon]) -> Floor:
        """Return the completed floor"""
        self._floor.dungeon = dungeon  # Pass dungeon reference.
        return self._floor
    
    
    def _get_tunnel_set(
        self,
        r1_cell: tuple[int, int],
        r2_cell: tuple[int, int]
    ) -> set[tuple[int, int]]:
        """Get the set of individual tunnel sets that form an L-shape that
        connects two rooms.
        """
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

