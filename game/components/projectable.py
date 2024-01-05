from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from ..engine import Engine
    from ..gamestates import State
    from ..dungeon.floor import Floor
from ..entities import Entity, Item, Creature, Player
from ..actions import Action, ItemAction
from .base_component import BaseComponent


# TODO if enemies are able to wield weapons in the future, change to account
# for enemy or player wielding it.
# TODO add expend magicka function on fighter component.
# TODO take turn after casting projectable.
# TODO can't cast at corpses.
class Projectable(BaseComponent):
    """An item that is able to project something at a target cell"""

    def __init__(self, uses: int, magicka_cost: int):
        self._uses_left = uses
        self._magicka_cost = magicka_cost
    
    @property
    def uses_left(self) -> int:
        return self._uses_left
    
    @property
    def magicka_cost(self) -> int:
        return self._magicka_cost
    
    def get_entity_at_target(self, 
                             floor: Floor, 
                             tiles_in_fov: dict[tuple[int, int]], 
                             x: int, y: int) -> Optional[Entity]:
        """Get the entity at target position if there is one"""
        # TODO fix the one-off thing with indices in terminal file.
        for entity in floor.entities:
            if entity.x == x - 1 and entity.y == y - 1:
                return entity
        return None


    def expend_use(self) -> None:
        self._uses_left -= 1

    def get_action_or_state(self, projector: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on projecting from item"""
        return ItemAction(projector, self.owner)
    
    def perform(self, engine: Engine) -> None:
        """Project from item"""
        pass  # Overridable.


class LightningProjectable(Projectable):
    """An item that shoots out a powerful burst of lightning"""

    def __init__(self, uses: int, magicka_cost: int, damage: int):
        super().__init__(uses, magicka_cost)
        self._damage = damage
    
    def perform(self, engine: Engine) -> None:
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.tiles_in_fov,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )
        
        if not entity:
            engine.message_log.add("Can't strike at nothing")
            return
        
        # TODO vaporize the item.
        if isinstance(entity, Item):
            engine.message_log.add("Can't strike at an item")
            return
        
        if isinstance(entity, Player):
            engine.message_log.add("Don't strike yourself. Are you okay?")
            return

        if isinstance(entity, Creature):
            engine.message_log.add(
                f"You cast a bolt of lightning at {entity.name}...")
            entity.fighter.take_damage(self._damage)
            self.owner.parent.fighter.magicka -= self.magicka_cost
            engine.message_log.add(f"for {self._damage} pts!")

        self.expend_use()


class HealingProjectable(Projectable):
    """An item that shoots out a healing orb"""

    def __init__(self, uses: int, magicka_cost: int, heal: int):
        super().__init__(uses, magicka_cost)
        self._heal = heal
    
    def perform(self, engine: Engine) -> None:
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.tiles_in_fov,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )

        if not entity:
            engine.message_log.add("Can't heal nothing")
            return
        
        if isinstance(entity, Item):
            engine.message_log.add("Can't heal an item")
            return
        
        if isinstance(entity, Player):
            engine.message_log.add("You cast the healing orb on yourself")
            entity.fighter.heal(self._heal)
            entity.fighter.magicka -= self.magicka_cost
            engine.message_log.add(
                f"You regained {self._heal} pts!", color="blue")
            self.expend_use()
            return

        if isinstance(entity, Creature):
            engine.message_log.add(
                f"You cast the healing orb on {entity.name}")
            entity.fighter.heal(self._heal)
            self.owner.parent.fighter.magicka -= self.magicka_cost
            engine.message_log.add(
                f"It regained {self._heal} pts!", color="blue")

        self.expend_use()

                                                              