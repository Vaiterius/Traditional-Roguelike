from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from ..engine import Engine
    from ..gamestates import State
    from ..dungeon.floor import Floor
from ..entities import Entity, Item, Creature, Player
from ..actions import Action, ItemAction
from ..render_order import RenderOrder
from .base_component import BaseComponent
from .ai import AllyFollowingAI, AllyDefendingAI, ConfusedAI, FrozenAI


# TODO if enemies are able to wield weapons in the future, change to account
# for enemy or player wielding it.
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
                             x: int, y: int) -> Optional[Entity]:
        """Get the entity at target position if there is one"""
        # Off by one index due to game data vs curses window representation.
        # Reversed to sort for creatures first.
        for entity in reversed(floor.entities):
            if entity.x == x - 1 and entity.y == y - 1:
                return entity
        return None

    def expend_use(self) -> None:
        self._uses_left -= 1

    def get_action_or_state(self, projector: Creature) -> Union[Action, State]:
        """Get an action or state to be performed on projecting from item"""
        return ItemAction(projector, self.owner)
    
    # Overridable.
    def perform(self, engine: Engine) -> bool:
        """Project from item"""
        # If impossible.
        # If item.
        # If corpse.
        # If self.
        # If valid target.
        pass


class DamagingProjectable(Projectable):
    """Deal some damage when projected at a target"""

    def __init__(self, uses: int, magicka_cost: int, magic_damage: int):
        super().__init__(uses, magicka_cost)
        self._magic_damage = magic_damage


class EffectPerTurnProjectable(Projectable):
    """
    Cast an effect or debuff on an enemy, lasting however many turns specified
    """

    def __init__(self, uses: int, magicka_cost: int, turns_remaining: int):
        super().__init__(uses, magicka_cost)
        self._turns_remaining = turns_remaining


class LightningProjectable(DamagingProjectable):
    """An item that shoots out a powerful burst of lightning"""

    def __init__(self, uses: int, magicka_cost: int, magic_damage: int):
        super().__init__(uses, magicka_cost, magic_damage)
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )
        
        if not entity:
            engine.message_log.add("Nothing to strike at here")
            return turnable

        if isinstance(entity, Item):
            self.expend_use()
            engine.dungeon.current_floor.entities.remove(entity)

            engine.message_log.add(
                f"The {entity.name} vaporizes!",
                color="blue"
            )

            del entity
            turnable = True
            return turnable
        
        if entity.render_order == RenderOrder.CORPSE:
            engine.message_log.add("Stop, it's already dead!")
            return turnable
        
        if isinstance(entity, Player):
            engine.message_log.add("Don't strike yourself. Are you okay?")
            return turnable

        if isinstance(entity, Creature):
            self.expend_use()
            engine.message_log.add(
                f"You cast a bolt of lightning at {entity.name}...",
                color="blue"
            )
            entity.fighter.take_damage(self._magic_damage)
            self.owner.parent.fighter.magicka -= self.magicka_cost
            engine.message_log.add(f"for {self._magic_damage} pts!")
            turnable = True

        return turnable


# TODO Fireball projectable - sets them on fire for x turns, may spread.


class HealingProjectable(Projectable):
    """An item that shoots out a healing orb"""

    def __init__(self, uses: int, magicka_cost: int, heal: int):
        super().__init__(uses, magicka_cost)
        self._heal = heal
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )

        if not entity:
            engine.message_log.add("Nothing to heal here")
            return turnable
        
        if isinstance(entity, Item):
            engine.message_log.add("That item isn't broken")
            return turnable
        
        if entity.render_order == RenderOrder.CORPSE:
            engine.message_log.add("Doing that isn't going to bring it back")
            return turnable
        
        if entity.fighter.health >= entity.fighter.max_health:
            engine.message_log.add("Health is already full!")
            return turnable
        
        if isinstance(entity, Player):
            self.expend_use()
            engine.message_log.add(
                "You cast the healing orb on yourself", color="blue")
            
            difference: int = self.owner.parent.fighter.health
            entity.fighter.heal(self._heal)
            entity.fighter.magicka -= self.magicka_cost
            difference -= self.owner.parent.fighter.health

            engine.message_log.add(
                f"You regained {difference} pts!", color="blue")
            
            turnable = True
            return turnable

        if isinstance(entity, Creature):
            self.expend_use()
            engine.message_log.add(
                f"You cast the healing orb on {entity.name}")
            
            difference: int = entity.fighter.health
            entity.fighter.heal(self._heal)
            self.owner.parent.fighter.magicka -= self.magicka_cost
            difference -= entity.fighter.health

            engine.message_log.add(
                f"It regained {abs(difference)} pts!", color="blue")
            turnable = True

        return turnable


class RizzProjectable(EffectPerTurnProjectable):
    """
    Cast a spell to rizz up an enemy, following you around the floor and
    fighting other enemies with you
    """

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )

        if not entity:
            engine.message_log.add("Nothing to rizz up here")
            return turnable
        
        if isinstance(entity, Item):
            engine.message_log.add("Your rizz fails on this item")
            return turnable
        
        if entity.render_order == RenderOrder.CORPSE:
            engine.message_log.add("Doing that isn't going to bring it back")
            return turnable
        
        if isinstance(entity, Player):
            engine.message_log.add("Can't rizz up yourself")
            return turnable
        
        if isinstance(entity, Creature):
            if isinstance(entity.ai, (AllyDefendingAI, AllyFollowingAI)):
                engine.message_log.add(
                    f"{entity.name} is already rizzed up!")
                return turnable
            
            self.expend_use()
            entity.add_component(
                "ai",
                AllyFollowingAI(
                    entity, 
                    entity.ai, 
                    self._turns_remaining, 
                    entity.color
                )
            )
            
            engine.message_log.add(
                f"{entity.name} is temporarily swayed by your rizz!",
                color="blue"
            )

            self.owner.parent.fighter.magicka -= self.magicka_cost
            turnable = True
        
        return turnable



class ConfusionProjectable(EffectPerTurnProjectable):
    """
    Cast a spell to confuse an enemy, stumbling around and bumping into other
    living things
    """
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )

        if not entity:
            engine.message_log.add("Nothing to confuse here")
            return turnable
        
        if isinstance(entity, Item):
            engine.message_log.add("The item refuses to be confused")
            return turnable
        
        if entity.render_order == RenderOrder.CORPSE:
            engine.message_log.add("The corpse is just as confused as you are")
            return turnable
        
        if isinstance(entity, Player):
            engine.message_log.add(
                "Confused, your actions are. Confusion, you shall not be.")
            return turnable

        if isinstance(entity, Creature):
            if isinstance(entity.ai, ConfusedAI):
                engine.message_log.add(f"{entity.name} is already confused!")
                return turnable
            
            self.expend_use()
            entity.add_component(
                "ai", ConfusedAI(entity, entity.ai, self._turns_remaining))

            engine.message_log.add(
                f"You cast a wave of bewilderment upon {entity.name}, now "
                "stumbling around", color="blue"
            )

            self.owner.parent.fighter.magicka -= self.magicka_cost
            turnable = True

        return turnable


class RageProjectable(EffectPerTurnProjectable):
    """Cast a spell to enrage an enemy, attacking any living thing on sight.
    
    Also temporarily buffs stats.
    """

    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        return turnable


class FreezeProjectable(EffectPerTurnProjectable):
    """Cast a spell to freeze an enemy in place"""
    
    def perform(self, engine: Engine) -> bool:
        turnable: bool = False
        entity: Optional[Entity] = self.get_entity_at_target(
            engine.dungeon.current_floor,
            engine.gamestate.cursor_index_x,
            engine.gamestate.cursor_index_y
        )

        if not entity:
            engine.message_log.add("Nothing to freeze here")
            return turnable
        
        if isinstance(entity, Item):
            engine.message_log.add("Did you think this item was gonna move?")
            return turnable
        
        if entity.render_order == RenderOrder.CORPSE:
            engine.message_log.add(
                "The corpse isn't going anywhere, don't worry")
            return turnable
        
        if isinstance(entity, Player):
            engine.message_log.add("You can't play freeze tag with yourself")
            return turnable
        
        if isinstance(entity, Creature):
            if isinstance(entity.ai, FrozenAI):
                engine.message_log.add(f"{entity.name} is already frozen!")
                return turnable
            
            self.expend_use()
            entity.add_component(
                "ai", FrozenAI(entity, entity.ai, self._turns_remaining))

            engine.message_log.add(
                f"{entity.name} stops in its tracks, completely unable to"
                "move", color="blue"
            )

            self.owner.parent.fighter.magicka -= self.magicka_cost
            turnable = True

        return turnable

                                                              