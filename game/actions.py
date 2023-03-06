from .entities import Creature


class Action:
    def perform():
        pass


class ActionWithDirection:

    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.dx = dx
        self.dy = dy


class WalkAction(ActionWithDirection):

    def perform(self, engine: "Engine", creature: Creature):
        floor = engine.dungeon.current_floor

        desired_x = creature.x + self.dx
        desired_y = creature.y + self.dy

        # Get within bounds.
        # Get blocking tiles.
        if not floor.tiles[desired_x][desired_y].walkable:
            return
        # Get blocking entities.

        creature.move(dx=self.dx, dy=self.dy)

