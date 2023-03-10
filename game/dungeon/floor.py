from __future__ import annotations

from typing import Iterator, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon import Dungeon
    from .room import Room
    from ..entities import Item, Player
    from ..tile import Tile
from ..entities import Creature


class Floor:
    """A dungeon floor of rooms filled with objects, entities, and you"""

    def __init__(self,
                 width: int,
                 height: int,
                 dungeon: Dungeon,
                 tiles: list[list[Tile]],
                 rooms: list[Room],
                 entities: list[Union[Player, Creature, Item]]):
        self.width = width
        self.height = height

        self.dungeon = dungeon

        self.tiles = tiles

        self.rooms = rooms

        self.entities = entities
    
    @property
    def items(self) -> Iterator[Item]:
        pass
    
    @property
    def creatures(self) -> Iterator[Creature]:
        yield from (
            entity for entity in self.entities
            if isinstance(entity, Creature)
        )
    
    @property
    def unexplored_rooms(self) -> Iterator[Room]:
        yield from (room for room in self.rooms if not room.explored)
    
    @property
    def first_room(self) -> Room:
        return self.rooms[0]
    
    @property
    def last_room(self) -> Room:
        return self.rooms[-1]


    def blocking_entity_at(
        self, x: int, y: int) -> Optional[Union[Player, Creature]]:
        """Check if a cell is occupied by an entity"""
        for entity in self.entities:
            if entity.x == x and entity.y == y and entity.blocking:
                return entity
        return None