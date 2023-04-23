from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .components.base_component import BaseComponent
    from .color import Color
    from .engine import Engine
    from .dungeon.floor import Floor
from .render_order import RenderOrder


class Entity:
    """A generic entity that creatures and objects derive from"""
    
    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 render_order: RenderOrder,
                 blocking: bool):
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.render_order = render_order
        self.blocking = blocking
    

    def get_component(self, name: str) -> Optional[BaseComponent]:
        return getattr(self, name, None)
    

    def add_component(self, name: str, component: BaseComponent) -> None:
        component.owner = self
        setattr(self, name, component)
    

    def del_component(self, name: str) -> None:
        delattr(self, name)
    
    def spawn_clone(self) -> Entity:
        return copy.deepcopy(self)


class Item(Entity):
    """A holdable or usable thing to a creature"""
    parent: Optional[Creature]
    
    def place(self, floor: Floor, x: int, y: int) -> None:
        """Place this somewhere on the map"""
        floor.add_entity(self)

        self.x = x
        self.y = y


class Creature(Entity):
    """A moving, living, wandering thing"""

    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 render_order: RenderOrder,
                 blocking: bool = True,
                 energy: int = 0):
        super().__init__(x, y, name, char, color, render_order, blocking)
        self.og_name = name  # Track old name after name change upon death.
        self.energy_gain_per_turn = energy
        self.energy = energy
    

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
    
    
    def take_turn(self, engine: Engine) -> None:
        """If monster has enough energy, perform its turn"""
        ENERGY_THRESHOLD: int = 10
        if self.ai:
            self.energy += self.energy_gain_per_turn
            if self.energy >= ENERGY_THRESHOLD:
                self.ai.perform(engine)
                self.energy -= ENERGY_THRESHOLD  # Expend energy.


class Player(Creature):
    """A special and heroic creature controlled by you, Player"""

