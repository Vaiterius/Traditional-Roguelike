from __future__ import annotations

import bisect
from typing import Iterator, Optional, Union, Generator, TYPE_CHECKING

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

        # If applicable (normal mode, last floor) - track relic/glyph rooms.
        self.relic_room: Optional[Room] = None
        self.glyphs_room: Optional[Room] = None
        self.passage_revealed: bool = False
    
    
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
    

    def entity_at(self, x: int, y: int) -> Optional[Entity]:
        """Check if a cell is occupied by any entity"""
        for entity in self.entities:
            if isinstance(entity, Player):
                continue
            if entity.x == x and entity.y == y:
                return entity
        return None
    
    
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
    """Methods to build and customize dungeon levels step-by-step.
    
    Includes additional functionality for final floor making on normal mode.
    Decided not to create another floorbuilder class for that.
    """
    
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

        # Yes, this is repeated again from self._floor, I'm just too lazy to 
        # change all the references.
        self.relic_room: Optional[Room] = None
        self.glyphs_room: Optional[Room] = None
    
    
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


    def place_relic_room(
            self, tile_type: Tile = floor_tile_shrouded) -> FloorBuilder:
        """QUEST - place on a random corner of the map.
        
        Must be called before place_rooms()
        """
        height: int = 5
        width: int = 9

        room = Room(
            rng=self.rng,
            # Pick if bottom or top corner.
            x1=self.rng.choice([1, self.floor_height - height - 1]),
            # Pick if left or right corner.
            y1=self.rng.choice([1, self.floor_width - width - 1]),
            width=width,
            height=height,
            floor=self._floor
        )

        self._dig_room(room, tile_type)
        self._floor.rooms.append(room)
        self._floor.relic_room = room
        self.relic_room = room

        return self
    

    def place_glyphs_room(
        self,
        spawner: Spawner,
        tile_type: Tile = floor_tile_shrouded
    ) -> FloorBuilder:
        """QUEST - place next to the relic room.
        
        Must be called after place_relic_room()
        """
        height: int = 4
        width: int = 7
        x1: int = -1
        y1: int = -1

        if not self.relic_room:
            return self

        # Place next to relic room respective to where it was randomly placed
        # in a corner.

        # Set the top-left tip of glyphs room on any of these coordinates.
        room_tip: tuple[int, int] = (-1, -1)
        possible_tip_placements = set()
        OFFSET: int = 2  # Space between relic and glyph rooms.

        # Relic room is on:
        # Top left corner.
        if self.relic_room.x1 == 1 and self.relic_room.y1 == 1:
            # Get coordinates along bottom and right sides.
            possible_tip_placements.update(
                # Bottom side - from left to right.
                self._find_points_between(
                    (self.relic_room.x2 + OFFSET, self.relic_room.y1),
                    (self.relic_room.x2 + OFFSET, self.relic_room.y2 + OFFSET)
                )
            )
            possible_tip_placements.update(
                # Right side - from top to bottom.
                self._find_points_between(
                    (self.relic_room.x1, self.relic_room.y2 + OFFSET),
                    (self.relic_room.x2 + OFFSET, self.relic_room.y2 + OFFSET)
                )
            )
            # Top-left corner tip can be set anywhere along placements.
            room_tip = self.rng.choice(list(possible_tip_placements))

        # Top right corner.
        elif (
            self.relic_room.x1 == 1
            and self.relic_room.y1 == self.floor_width - self.relic_room.width - 1
        ):
            # Get coordinates along bottom and left sides.
            possible_tip_placements.update(
                self._find_points_between(
                    # Bottom side - from left to right.
                    (self.relic_room.x2 + OFFSET, self.relic_room.y1 - OFFSET),
                    (self.relic_room.x2 + OFFSET, self.relic_room.y2)
                )
            )
            possible_tip_placements.update(
                self._find_points_between(
                    # Left side - from top to bottom.
                    (self.relic_room.x1, self.relic_room.y1 - OFFSET),
                    (self.relic_room.x2 + OFFSET, self.relic_room.y1 - OFFSET)
                )
            )
            # Offset for top-right corner tip.
            room_tip = self.rng.choice(list(possible_tip_placements))
            room_tip = (room_tip[0], room_tip[1] - width)

        # Bottom left corner.
        elif (
            self.relic_room.x1 == self.floor_height - self.relic_room.height - 1
            and self.relic_room.y1 == 1
        ):
            # Get coordinates along top and right sides.
            possible_tip_placements.update(
                self._find_points_between(
                    # Top side - from left to right.
                    (self.relic_room.x1 - OFFSET, self.relic_room.y1),
                    (self.relic_room.x1 - OFFSET, self.relic_room.y2 + OFFSET)
                )
            )
            possible_tip_placements.update(
                self._find_points_between(
                    # Right side - from top to bottom.
                    (self.relic_room.x1, self.relic_room.y2 + OFFSET),
                    (self.relic_room.x2, self.relic_room.y2 + OFFSET)
                )
            )
            # Offset for bottom-left corner tip.
            room_tip = self.rng.choice(list(possible_tip_placements))
            room_tip = (room_tip[0] - height, room_tip[1])

        # Bottom right corner.
        elif (
            self.relic_room.x1 == self.floor_height - self.relic_room.height - 1
            and self.relic_room.y1 == self.floor_width - self.relic_room.width - 1
        ):
            # Get coordinates along top and left sides.
            possible_tip_placements.update(
                self._find_points_between(
                    # Top side - from left to right.
                    (self.relic_room.x1 - 2, self.relic_room.y1 - 2),
                    (self.relic_room.x1 - 2, self.relic_room.y2)
                )
            )
            possible_tip_placements.update(
                self._find_points_between(
                    # Left side - from top to bottom.
                    (self.relic_room.x1 - 2, self.relic_room.y1 - 2),
                    (self.relic_room.x2, self.relic_room.y1 - 2)
                )
            )
            # Offset for bottom right corner tip.
            room_tip = self.rng.choice(list(possible_tip_placements))
            room_tip = (room_tip[0] - height, room_tip[1] - width)

        # Should not happen.
        else:
            return self
        
        x1, y1 = room_tip

        room = Room(
            rng=self.rng,
            x1=x1,
            y1=y1,
            width=width,
            height=height,
            floor=self._floor
        )

        self._dig_room(room, tile_type)
        self._floor.rooms.append(room)
        self._floor.glyphs_room = room
        self.glyphs_room = room

        # Place pedestals.
        spawner.spawn_furniture_at((x1 + 1, y1 + 1), room, "Pedestal")
        spawner.spawn_furniture_at((x1 + 1, y1 + 5), room, "Pedestal")
        spawner.spawn_furniture_at((x1 + 2, y1 + 3), room, "Pedestal")

        return self
    
    
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

            self._dig_room(room, tile_type)
            
            self._floor.rooms.append(room)
        
        return self
    

    def reverse_rooms(self) -> FloorBuilder:
        """
        QUEST - Ensure relic room is the last room in list order.

        Must be called before placing tunnels and after placing all rooms
        """
        self._floor.rooms.reverse()
        return self
    
    
    def place_tunnels(self, tile_type: Tile = floor_tile_dim, vertical_first: bool = True) -> FloorBuilder:
        """Build a tunnel path from one room to the next"""
        rooms: list[Room] = self._floor.rooms

        if self.relic_room is not None:  # Leave relic room untunneled.
            rooms.remove(self.relic_room)

        for index, room in enumerate(rooms):

            if index == len(rooms) - 1:  # On final room.
                break

            if len(rooms) > 1:
                # Dig tunnel from this room to previous room.
                r1_cell = room.get_random_cell()
                r2_cell = rooms[index + 1].get_random_cell()

                # Decide whether first tunnel leg is vertical or horizontal.
                if vertical_first:
                    tunnel_set = self.get_tunnel_set_1(r1_cell, r2_cell)
                else:
                    tunnel_set = self.get_tunnel_set_2(r1_cell, r2_cell)
                
                # Don't allow any tunnel to meet with the relic room.
                if self.relic_room:
                    for coord in tunnel_set:

                        # Original first tunnel leg choice invalid/intersects,
                        # so switch tunnel legs. Guarenteed to never intersect
                        # with the relic room.
                        if self.relic_room.intersects_with_point(coord):
                            if vertical_first:
                                tunnel_set = self.get_tunnel_set_2(
                                    r1_cell, r2_cell)
                            else:
                                tunnel_set = self.get_tunnel_set_1(
                                    r1_cell, r2_cell)

                self.dig_tunnel(self._floor, tunnel_set)
        
        if self.relic_room:
            self._floor.rooms.append(self.relic_room)  # Add back.
        
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
    

    @staticmethod
    def dig_tunnel(
        floor: Floor,
        tunnel_set: set[tuple[int, int]],
        tile_type: Tile = floor_tile_dim
    ) -> None:
        """Dig through the desired tunnel path from point a to point b"""
        for x, y in tunnel_set:
            floor.tiles[x][y] = tile_type
            # Track for pathfinding.
            floor.wall_locations -= {(x, y)}
        
    

    def _find_points_between(
            self, coord1: tuple[int, int], coord2: tuple[int, int]) -> set:
        """Returns all points between two coordinates.
        
        Horizontal or vertical lines only.
        """
        points: list[tuple[int, int]] = []

        x1, y1 = coord1
        x2, y2 = coord2

        if y1 == y2:  # Horizontal alignment.
            points.extend(
                [
                    (x, y1)
                    for x in
                    range(min(x1, x2), max(x1, x2) + 1)
                ]
            )
        elif x1 == x2:  # Vertical alignment.
            points.extend(
                [
                    (x1, y)
                    for y in
                    range(min(y1, y2), max(y1, y2) + 1)
                ]
            )
        
        return set(points)
    

    def _dig_room(
        self,
        room: Room,
        tile_type: Tile = floor_tile_shrouded
    ) -> None:
        """Carve out the walls for a room"""
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                self._floor.tiles[x][y] = tile_type
                # Track for pathfinding.
                self._floor.wall_locations.remove((x, y))


    #####
    # After spending my ENTIRE Sunday trying to change from vertical leg first
    # to horizontal leg first, implemented in the following two functions,
    # please do not touch the logic below. Holy shit.
    #####
    

    @staticmethod
    def get_tunnel_set_1(
        r1_cell: tuple[int, int],
        r2_cell: tuple[int, int]
    ) -> set[tuple[int, int]]:
        """
        Get the set of individual tunnel sets that form an L-shape that
        connects two rooms.

        First leg goes vertically, second leg goes horizontally.
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
        # Switch endpoints if room 1 is right of room 2.
        if r1_cell_y >= r2_cell_y:
            start_y, end_y = end_y, start_y
        
        # Create y-axis coordinates from end of leg 1.
        for y in range(start_y, end_y + 1):
            tunnel_set.add((end_x, y))
        
        return tunnel_set
    

    @staticmethod
    def get_tunnel_set_2(
        r1_cell: tuple[int, int],
        r2_cell: tuple[int, int]
    ) -> set[tuple[int, int]]:
        """
        Get the set of individual tunnel sets that form an L-shape that
        connects two rooms.

        First leg goes horizontally, second leg goes vertically.
        """
        tunnel_set = set()
        r1_cell_x, r1_cell_y = r1_cell
        r2_cell_x, r2_cell_y = r2_cell

        # Room 1 is to the left of room 2.
        start_y = r1_cell_y
        end_y = r2_cell_y
        # Switch endpoints if room 2 is left of room 1.
        if r1_cell_y >= r2_cell_y:
            start_y, end_y = end_y, start_y
        
        # Room 1 is above room 2.
        start_x = r1_cell_x
        end_x = r2_cell_x
        # Switch endpoints if room 1 is below room 2.
        if r1_cell_x >= r2_cell_x:
            start_x, end_x = end_x, start_x
        
        # Create y-axis coordinates, forming leg 1.
        for y in range(start_y, end_y + 1):
            if start_x == r1_cell_x:
                tunnel_set.add((r1_cell_x, y))
            else:
                tunnel_set.add((r2_cell_x, y))
        
        # Create x-axis coordinates from end of leg 1.
        for x in range(start_x, end_x + 1):
            if start_x == r1_cell_x:
                tunnel_set.add((x, r2_cell_y))
            else:
                tunnel_set.add((x, r1_cell_y))
        
        return tunnel_set

