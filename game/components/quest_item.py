from .base_component import BaseComponent


class QuestItem(BaseComponent):
    """
    Indicate that the item is involved in the main quest
    """


class Relic(QuestItem):
    """To be fetched back up to the entrance"""


class Glyph(QuestItem):
    """To be combined to reveal the hidden room"""

