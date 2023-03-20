import bisect
from enum import Enum, auto


class Entity:
    def __init__(self, name, render_order):
        self.name = name
        self.render_order = render_order
    
    def __repr__(self):
        return self.name


class RenderOrder(Enum):
    STAIRCASE = auto()
    ITEM = auto()
    CREATURE = auto()


entities = []
bisect.insort(entities, Entity("zombie1", RenderOrder.CREATURE), key=lambda x: x.render_order.value)
bisect.insort(entities, Entity("zombie2", RenderOrder.CREATURE), key=lambda x: x.render_order.value)
bisect.insort(entities, Entity("potion1", RenderOrder.ITEM), key=lambda x: x.render_order.value)
bisect.insort(entities, Entity("zombie3", RenderOrder.CREATURE), key=lambda x: x.render_order.value)
bisect.insort(entities, Entity("staircase", RenderOrder.STAIRCASE), key=lambda x: x.render_order.value)

print(entities)

potion2 = Entity("potion2", RenderOrder.ITEM)
bisect.insort(entities, potion2, key=lambda x: x.render_order.value)

print(entities)

entities.remove(potion2)

print(entities)
