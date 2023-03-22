from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .components.component import BaseComponent
    from .color import Color
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
                 blocking: bool,):
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


class Item(Entity):
    pass


class Creature(Entity):
    """A moving, living, wandering thing"""

    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 char: str,
                 color: Color,
                 render_order: RenderOrder,
                 hp: int,
                 dmg: int,
                 blocking: bool = True):
        super().__init__(x, y, name, char, color, render_order, blocking)
        self.og_name = name  # Track old name after name change upon death.
        self.max_hp = hp
        self.hp = hp  # Starting hp.
        self.dmg = dmg


    @property
    def is_dead(self) -> bool:
        return self.hp <= 0
    
    def set_hp(self, new_hp: int) -> None:
        # New HP cannot be lower than 0 or higher than max HP.
        self.hp = max(0, min(self.max_hp, new_hp))
        if self.is_dead:
            self.die()
    

    def die(self) -> None:
        """ RIP bozo"""
        # TODO Player dies.
        # Creature dies.
        self.ai = None
        self.blocking = False
        self.char = "%"
        self.name = f"Remains of {self.name}"
        self.render_order = RenderOrder.CORPSE


    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
    

    def spawn_clone(self) -> Creature:
        return copy.deepcopy(self)


class Player(Creature):
    """You!"""
    pass

