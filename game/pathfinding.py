from __future__ import annotations

# from queue import PriorityQueue
import heapq
from typing import TYPE_CHECKING, Iterator, TypeVar, Optional

if TYPE_CHECKING:
    from .dungeon.floor import Floor


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


# A-star PATHFINDING #

GridLocation = tuple[int, int]
T = TypeVar("T")


class WeightedFloorGrid:
    """Abstraction wrapper for Floor for A-star pathfinding purposes"""

    def __init__(self, floor: Floor):
        self._width = floor.width
        self._height = floor.height
        self._wall_locations: set[GridLocation] = floor.wall_locations
        self._weights: dict[GridLocation, float] = {}
    
    # def in_bounds(self, id: GridLocation) -> bool:
    #     x, y = id
    #     return 0 <= x < self._width and 0 <= y < self._height

    def passable(self, id: GridLocation) -> bool:
        return id not in self._wall_locations
    
    def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
        x, y = id
        neighbors: list[GridLocation] = [  # NW, N, NE, W, E, SW, S, SE.
            (x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1),
            (x, y + 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)
        ]
        # if (x + y) % 2 == 0:
        #     neighbors.reverse()
        # results = filter(self.in_bounds, neighbors)
        return filter(self.passable, neighbors)
    
    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        return self._weights.get(to_node, 1)


class PriorityQueue:
    def __init__(self):
        self._elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self._elements
    
    def put(self, item: T, priority: float) -> None:
        heapq.heappush(self._elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self._elements)[1]


def heuristic(a: GridLocation, b: GridLocation) -> float:
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(
        graph: WeightedFloorGrid,
        start: GridLocation,
        goal: GridLocation) -> dict[GridLocation, Optional[GridLocation]]:
    """
    Credits: https://www.redblobgames.com/pathfinding/a-star/implementation.html
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[GridLocation, Optional[GridLocation]] = {}
    cost_so_far: dict[GridLocation, float] = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: GridLocation = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost: float = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority: float = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from


def a_star_path_to(
        floor: Floor, x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    start: GridLocation = (x1, y1)
    goal: GridLocation = (x2, y2)
    graph: WeightedFloorGrid = WeightedFloorGrid(floor)
    came_from = a_star_search(graph, start, goal)

    current: GridLocation = goal
    path: list[GridLocation] = []
    if goal not in came_from:  # No path was found.
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    
    # Optionals.
    path.append(start)
    path.reverse()
    
    return path

