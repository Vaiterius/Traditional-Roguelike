import random

from ..entities import Creature
from ..config import enemies
from ..components.component import WanderingAI, HostileEnemyAI

class Spawner:

    # TODO
    @staticmethod
    def spawn_player():
        pass

    # TODO refactor dungeon and pass max_entities_per_room to method.
    @staticmethod
    def spawn_random_enemy_instance() -> object:
        enemy_data: dict = random.choices(
            population=list(enemies.values()),
            weights=[enemy["spawn_chance"] for enemy in enemies.values()]
        )[0]
        enemy = Creature(
            x=-1,
            y=-1,
            name=enemy_data["name"],
            char=enemy_data["char"],
            color=enemy_data["color"],
            hp=enemy_data["hp"],
            dmg=enemy_data["dmg"]
        )
        # enemy.add_component("ai", WanderingAI(enemy))
        enemy.add_component("ai", HostileEnemyAI(enemy))
        return enemy
    

    # TODO??
    @staticmethod
    def spawn_random_enemy_instances() -> list[object]:
        pass