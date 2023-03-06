from color import Color


class Entity:
    
    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 blocking: bool):
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.blocking = blocking


class Creature(Entity):

    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 max_hp: int,
                 blocking: bool = True):
        super().__init__(x, y, name, char, color, blocking)
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.max_hp = max_hp
        self.hp = max_hp  # Starting hp.

        self.blocking = blocking


    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy


class Player(Creature):

    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 max_hp: int,
                 blocking: bool = True):
        super().__init__(x, y, name, char, color, blocking)
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.max_hp = max_hp
        self.hp = max_hp

        self.blocking = blocking

