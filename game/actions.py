from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .entities import Creature, Entity


class Action:
    """Base action"""

    def __init__(self, entity: Entity):
        self.entity = entity

    def perform(self) -> None:
        """Overridable method"""
        pass


class WaitAction(Action):
    """Do nothing this turn"""

    def perform(self, engine: Engine) -> None:
        pass


class ActionWithDirection(Action):
    """Base action with x,y directioning"""

    def __init__(self, entity: Creature, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy


class BumpAction(ActionWithDirection):
    """Action to decide what happens when a creature moves to a desired tile"""

    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        if floor.blocking_entity_at(desired_x, desired_y):
            MeleeAction(self.entity, self.dx, self.dy).perform(engine)
        else:
            WalkAction(self.entity, self.dx, self.dy).perform(engine)


class WalkAction(ActionWithDirection):
    """Action to validly move a creature"""

    def perform(self, engine: Engine) -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        # Get within bounds.
        # Get blocking tiles.
        if not floor.tiles[desired_x][desired_y].walkable:
            return
        # Get blocking entities.
        if floor.blocking_entity_at(desired_x, desired_y):
            return

        self.entity.move(dx=self.dx, dy=self.dy)


class MeleeAction(ActionWithDirection):
    """Action to hit a creature within melee range"""

    def perform(self, engine: "Engine") -> None:
        floor = engine.dungeon.current_floor

        desired_x = self.entity.x + self.dx
        desired_y = self.entity.y + self.dy

        target: Entity = floor.blocking_entity_at(desired_x, desired_y)
        target.set_hp(target.hp - self.entity.dmg)

