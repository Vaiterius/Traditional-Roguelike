from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Generator

from .data.config import MAX_FOV_DISTANCE


def compute_fov(
    origin: tuple[int, int],
    is_blocking: callable[tuple[int, int], bool],
    mark_visible: callable[tuple[int, int], None]
) -> None:
    """Computes the field of view from an origin tile.
    
    Implemented using symmetric shadowcasting.
    Credits to: https://www.albertford.com/shadowcasting/
    """
    
    mark_visible(*origin)
    
    for i in range(4):
        quadrant = Quadrant(i, origin)
        
        
        def reveal(tile_pos) -> None:
            """Reveal a tile at a given coordinate"""
            x, y = quadrant.transform(tile_pos)
            if math.dist(origin, (x, y)) <= MAX_FOV_DISTANCE:
                mark_visible(x, y)
        
        
        def is_wall(tile_pos) -> bool:
            """Check if a given tile coordinate is a wall"""
            if tile_pos is None:
                return False
            x, y = quadrant.transform(tile_pos)
            return is_blocking(x, y)
        
        
        def is_floor(tile_pos) -> bool:
            """Check if a given tile coordinate is a floor"""
            if tile_pos is None:
                return False
            x, y = quadrant.transform(tile_pos)
            return not is_blocking(x, y)
        
        
        def scan(row: Row) -> None:
            """Scan a row and recursively scan all of its children.
            
            If you think of each quadrant as a tree of rows, this essentially
            is a depth-first tree traversal.
            """
            prev_tile: Optional[Row] = None
            for tile in row.tiles():
                if is_wall(tile) or is_symmetric(row, tile):
                    reveal(tile)
                if is_wall(prev_tile) and is_floor(tile):
                    row.start_slope = slope(tile)
                if is_floor(prev_tile) and is_wall(tile):
                    next_row = row.next()
                    next_row.end_slope = slope(tile)
                    scan(next_row)
                prev_tile = tile
            if is_floor(prev_tile):
                scan(row.next())
            
        first_row = Row(1, Fraction(-1), Fraction(1))
        scan(first_row)


class Quadrant:
    """Represent a 90-degree sector pointing north, south, east, west
    
    Traversed row by row. For the east and west quadrants, these "rows" are
    vertical, not horizontal.
    """
    
    north = 0
    east  = 1
    south = 2
    west  = 3


    def __init__(self, cardinal: int, origin: tuple[int, int]):
        self.cardinal = cardinal
        self.ox, self.oy = origin


    def transform(self, tile_pos: tuple[int, int]) -> tuple[int, int]:
        """
        Convert a (row, col) tuple representing a position relative to the
        current quadrant into an (x, y) tuple representing an absolute position
        in the grid
        """
        row, col = tile_pos
        if self.cardinal == Quadrant.north:
            return (self.ox + col, self.oy - row)
        if self.cardinal == Quadrant.south:
            return (self.ox + col, self.oy + row)
        if self.cardinal == Quadrant.east:
            return (self.ox + row, self.oy + col)
        if self.cardinal == Quadrant.west:
            return (self.ox - row, self.oy + col)


class Row:
    """Represent a segment a tiles bound between a start and end slope.
    
    `depth` represents the distance between the row and the quadrant's origin.
    """
    
    def __init__(self, depth: int, start_slope: Fraction, end_slope: Fraction):
        self.depth = depth
        self.start_slope = start_slope
        self.end_slope = end_slope
    
    
    def tiles(self) -> Generator[tuple[int, int]]:
        """Return an iterator over the tiles in the row.
        
        This function considers a tile to be in the row if the sector swept out
        by the row's start and end slopes overlaps with a diamond inscribed in
        the tile. If the diamond is only tangent to the sector, it does not
        become part of the row.
        """
        min_col: int = round_ties_up(self.depth * self.start_slope)
        max_col: int = round_ties_down(self.depth * self.end_slope)
        for col in range(min_col, max_col + 1):
            yield (self.depth, col)
    
    
    def next(self) -> Row:
        """Get the next row after the current one"""
        return Row(self.depth + 1, self.start_slope, self.end_slope)
    
    
def slope(tile_pos: tuple[int, int]) -> Fraction:
    """Calculate the new start and end slopes.
    
    Used in two situations:
    [1] if prev_tile (on the left) was a wall tile
    and tile (on the right) is a floor tile, then the slope represents a
    start slope and should be tangent to the right edge of the wall tile.
    [2] if prev_tile was a floor tile and tile is a wall tile, then the
    slope represents an end slope and should be tangent to teh left edge of
    the wall tile.
    
    In both situations, the line is tangent to the left edge of the current
    tile, so we can use a single slope function for both start and end
    slopes.
    """
    row_depth, col = tile_pos
    return Fraction(2 * col - 1, 2 * row_depth)


def is_symmetric(row: Row, tile_pos: tuple[int, int]):
    """Check if the given floor tile can be seen symmetrically from the origin.
    
    It returns true if the central point of the tile is in the sector swept out
    by the row's start and end slopes. Otherwise, it returns false.
    """
    row_depth, col = tile_pos
    return (
        col >= row.depth * row.start_slope and col <= row.depth * row.end_slope
    )


def round_ties_up(n) -> int:
    return math.floor(n + 0.5)


def round_ties_down(n) -> int:
    return math.ceil(n - 0.5)

