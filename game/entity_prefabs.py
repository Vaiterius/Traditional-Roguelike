from .entities import Creature
from .components.component import WanderingAI

ghoul = Creature(
    x=-1,
    y=-1,
    name="Ghoul",
    char='g',
    color="red",
    hp=6,
    dmg=2
)
ghoul.add_component("ai", WanderingAI(ghoul))

rat = Creature(
    x=-1,
    y=-1,
    name="Giant Rat",
    char='r',
    color="white",
    hp=2,
    dmg=1
)
rat.add_component("ai", WanderingAI(rat))
