from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..entities import Player
    from ..spawner import Spawner
    from ..rng import RandomNumberGenerator
    from ..components.inventory import Inventory
from ..components.quest_item import Glyph
from .floor import Floor, FloorBuilder
from ..data.config import NUM_FLOORS


@dataclass
class DungeonConfig:
    num_floors: int  # Only used by normal mode dungeon.
    max_enemies_per_floor: int
    max_items_per_floor: int
    floor_height: int
    floor_width: int
    min_num_rooms: int
    max_num_rooms: int
    min_room_height: int
    max_room_height: int
    min_room_width: int
    max_room_width: int


class Dungeon:
    """The underground complex of multiple floors, each one
    procedurally-generated with interconnected rooms filled with various loot
    and monsters.

    Floors are only generated once the player reaches a new depth, and not all
    at once.
    
    Subclassed into Normal and Endless mode dungeons.
    """

    def __init__(
        self,
        rng: RandomNumberGenerator,
        spawner: Spawner,
        config: DungeonConfig
    ):
        self._rng = rng
        self._config = config

        self.spawner = spawner
        self.floors: list[Floor] = []
        self.current_floor_index: int = 0
    
    @property
    def current_floor(self) -> Floor:
        return self.floors[self.current_floor_index]
    
    @property
    def on_first_floor(self) -> bool:
        return self.current_floor_index == 0
    
    @property
    def deepest_floor_index(self) -> int:
        """The deepest floor the player has currently reached"""
        return len(self.floors) - 1
    
    @property
    def can_ascend(self) -> bool:
        """Indicates which floors to put an ascending staircase on"""
        return True
    
    @property
    def can_descend(self) -> bool:
        """Indicates which floors to put a descending staircase on"""
        return True
    
    def spawn_player(self, player: Player) -> None:
        """Place player in middle of first room"""
        self.spawner.spawn_player(player, self.current_floor.first_room)
    
    def start(self) -> None:
        """Prepare and generate the dungeon's first floor"""

        # Regenerate if dungeon already exists.
        if self.floors:
            self.floors = []
            self.current_floor_index = 0
        
        self.generate_next_floor()
    
    def build_floor(
        self, num_rooms: int, can_descend: bool, can_ascend: bool) -> Floor:
        """Construct the map for the current dungeon level"""
        return (
            FloorBuilder(
                rng=self._rng,
                floor_height=self._config.floor_height,
                floor_width=self._config.floor_width
            )
            .place_walls()
            .place_rooms(
                num_rooms=num_rooms,
                min_room_height=self._config.min_room_height,
                max_room_height=self._config.max_room_height,
                min_room_width=self._config.min_room_width,
                max_room_width=self._config.max_room_width
            )
            .place_tunnels()
            .place_staircases(
                spawner=self.spawner,
                descending=can_descend,
                ascending=can_ascend
            )
            .place_items(
                spawner=self.spawner,
                max_items_per_floor=self._config.max_items_per_floor
            )
            .place_creatures(
                spawner=self.spawner,
                max_creatures_per_floor=self._config.max_enemies_per_floor
            )
            .build(self)
        )
    
    # Overridable.
    def generate_next_floor(self) -> Floor:
        """Dynamically generate the next floor"""
        pass


class NormalDungeon(Dungeon):
    """The dungeon for normal 'story' mode.
    
    Includes a quest service that requires the player to fetch the relic on
    the final floor inside a hidden room. The hidden room can only be revealed
    once the player activates 3 other relics scattered randomly throughout the
    previous floors.
    """

    def __init__(
        self,
        rng: RandomNumberGenerator,
        spawner: Spawner,
        config: DungeonConfig
    ):
        super().__init__(rng, spawner, config)

        # Determine which floor indices to spawn glyphs on.
        self.glyph_floor_indices: list[int] = [-1, -1, -1]
        # Floor indices between first and last, assuming at least 3 in between.
        numbers_between: list[int] = [num for num in range(1, NUM_FLOORS - 1)]
        for i in range(0, len(self.glyph_floor_indices)):
            floor_index: int = self._rng.choice(numbers_between)
            self.glyph_floor_indices[i] = floor_index
            numbers_between.remove(floor_index)
        
        self.pedestals_activated: int = 0

    @property
    def glyph_locations(self) -> str:
        locations: list[int] = [num + 1 for num in self.glyph_floor_indices]
        return f"{locations}"

    def floor_has_glyph(self, floor: Floor) -> bool:
        """Given floor has one or more glyphs"""
        for entity in floor.entities:
            if entity.get_component("glyph"):
                return True
        return False
    
    def count_glyphs_retrieved(self, inventory: Inventory) -> int:
        return inventory.count_instances_with_component("glyph")
    
    @property
    def on_last_floor(self) -> bool:
        return self.current_floor_index + 1 == self._config.num_floors
    
    @property
    def can_descend(self) -> bool:
        """Determine when to put descending staircases"""
        # Last descension is second-to-last floor.
        return not self.on_last_floor

    def build_floor(
        self, num_rooms: int, can_descend: bool, can_ascend: bool) -> Floor:
        """Construct the map for the current dungeon level"""
        builder: FloorBuilder = (
            FloorBuilder(
                rng=self._rng,
                floor_height=self._config.floor_height,
                floor_width=self._config.floor_width
            )
            .place_walls()
        )

        # Last floor will have the relic and glyph rooms.
        if self.on_last_floor:
            builder.place_relic_room().place_glyphs_room(self.spawner)

        return (
            builder.place_rooms(
                num_rooms=num_rooms,
                min_room_height=self._config.min_room_height,
                max_room_height=self._config.max_room_height,
                min_room_width=self._config.min_room_width,
                max_room_width=self._config.max_room_width
            )
            .reverse_rooms()  # Required.
            .place_tunnels()
            .place_staircases(
                spawner=self.spawner,
                descending=can_descend,
                ascending=can_ascend
            )
            .place_items(
                spawner=self.spawner,
                max_items_per_floor=self._config.max_items_per_floor
            )
            .place_creatures(
                spawner=self.spawner,
                max_creatures_per_floor=self._config.max_enemies_per_floor
            )
            .build(self)
        )
    
    def generate_next_floor(self) -> Floor:
        """Keep track of the ongoing quest status"""
        # Seeding floor procgen.
        self._rng.with_subseed(f"-floor-{self.current_floor_index + 1}")

        num_rooms: int = self._rng.randint(
            self._config.min_num_rooms, self._config.max_num_rooms)
        
        # Generate the interconnected rooms.
        floor: Floor = self.build_floor(
            num_rooms, self.can_descend, self.can_ascend)
        self.floors.append(floor)

        # Spawn one of the glyphs if in chosen index.
        if self.current_floor_index in self.glyph_floor_indices:
            self.spawner.spawn_item(
                self.current_floor.get_random_room(self._rng),
                item_type="glyph"
            )

        # TODO handle relic quest.
        if self.on_last_floor:
            self.spawner.spawn_item(floor.last_room, item_type="relic")
        
        return floor


class EndlessDungeon(Dungeon):
    """The dungeon for endless mode.
    
    This dungeon is limitless and can theoretically go on forever. There is no
    quest component - the player fights until they die.
    """

    def __init__(
        self,
        rng: RandomNumberGenerator,
        spawner: Spawner,
        config: DungeonConfig
    ):
        super().__init__(rng, spawner, config)
    
    @property
    def can_ascend(self) -> bool:
        """No away out of the dungeon!"""
        return self.current_floor_index != 0
    
    def generate_next_floor(self) -> Floor:
        """Dynamically generate the next floor"""
        # Seeding floor procgen.
        self._rng.with_subseed(f"-floor-{self.current_floor_index + 1}")

        num_rooms: int = self._rng.randint(
            self._config.min_num_rooms, self._config.max_num_rooms)
        
        # Generate the interconnected rooms.
        floor: Floor = self.build_floor(
            num_rooms, self.can_descend, self.can_ascend)
        self.floors.append(floor)

        return floor

