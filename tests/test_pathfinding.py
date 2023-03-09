import math
from time import sleep
from collections import namedtuple

Cell = namedtuple("Cell", "x, y")

grid = [[1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0]]

def print_grid(grid):
    grid_string = ""
    for row in grid:
        row_string = " ".join([str(cell) for cell in row])
        grid_string += row_string + "\n"
    print(grid_string)


def get_distance_from(start, end):
    return math.sqrt(((end.x - start.x) ** 2) + ((end.y - start.y)** 2))


def draw_path_brute(grid):
    # define current point (as starting point) and target point
    # define current distance
    # while current point is not target point do
        # brute force points around the current point
        # calculate distance
        # if distance is less than current distance do
            # set point as current point
            # set new best distance as current distance
    
    start_point = Cell(0, 0)
    end_point = Cell(4, 3)
    current_point = start_point
    current_distance = get_distance_from(current_point, end_point)
    paths = []
    while not (current_point.x == end_point.x and current_point.y == end_point.y):
        for x in range(current_point.x - 1, current_point.x + 2):
            for y in range(current_point.y -1, current_point.y + 2):
                try:
                    in_bounds = grid[x][y]
                    distance = get_distance_from(Cell(x, y), end_point)
                    if distance < current_distance:
                        current_point = Cell(x, y)
                        current_distance = distance
                        paths.append(current_point)
                        grid[x][y] = 1
                except IndexError:
                    continue
    for path in paths:
        print(f"({path.x}, {path.y})")


def draw_path_bresenham(grid):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = (0, 0)
    x2, y2 = (4, 3)
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
        grid[coord[0]][coord[1]] = 1
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


print_grid(grid)
# draw_path_brute(grid)
points = draw_path_bresenham(grid)
print(points)
print_grid(grid)
