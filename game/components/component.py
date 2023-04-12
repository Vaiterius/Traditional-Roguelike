from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import Entity

 
class BaseComponent:
    """A basic component, lives in an entity's component pack"""
    owner: Entity

