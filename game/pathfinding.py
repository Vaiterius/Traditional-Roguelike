from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Entity, Player
    from .dungeon.floor import Floor
from .entities import Creature



def distance_from(x1: int, y1: int, x2: int, y2: int) -> float:
    """Distance formula"""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def in_player_fov(
    player: Player, entity: Entity, floor: Floor) -> bool:
    """Return whether player is able to see an entity"""
    TILE_RANGE: int = 10
    
    # Able to see discovered items and other non-creatures on the map.
    if not isinstance(entity, Creature) and floor.tiles[entity.x][entity.y].explored:
        return True
    
    # Save resources and compute if within reasonable range.
    if distance_from(entity.x, entity.y, player.x, player.y) <= TILE_RANGE:

        # Line of sight is blocked.
        paths: list[tuple[int, int]] = bresenham_path_to(
            entity.x, entity.y, player.x, player.y)
        blocked: bool = any(
            [not floor.tiles[x][y].walkable for x,y in paths])
        
        if blocked or not floor.tiles[entity.x][entity.y].explored:
            return False
        
        return True
    return False


def bresenham_path_to(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    """Get a set coordinate points following a path to desired x and y.
    Useful for FOV and basic pathfinding.
    
    Uses Bresenham's algorithm from RogueBasin:
    http://www.roguebasin.com/index.php/Bresenham%27s_Line_Algorithm#Python
    """
    # Setup initial conditions
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points