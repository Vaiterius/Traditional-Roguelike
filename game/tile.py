class Tile:
    """Tile representation for each cell on the map"""
    
    def __init__(self, char: str, walkable: bool, explored: bool = False):
        self.char = char
        self.walkable = walkable
        self.explored = explored
