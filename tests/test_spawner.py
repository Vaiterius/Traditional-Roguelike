import random

from game.data.config import enemies

enemy_data: dict = random.choices(
    population=list(enemies.values()),
    weights=[enemy["spawn_chance"] for enemy in enemies.values()]
)
print(enemy_data)