import curses
from typing import Optional


class Color:
    """Colors for character tiles"""

    def __init__(self):
        curses.use_default_colors()

        # Initialize all character foreground colors.
        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        
        # TODO chance to enum? VALUE = code number
        self.supported_colors = {
            # Default colors.
            "black": 1,
            "red": 2,
            "green": 3,
            "yellow": 4,
            "blue": 5,
            "magenta": 6,
            "cyan": 7,
            "white": 8,
            
            # Custom colors.
            "off_white": 248,
            "grey": 241,
            "shrouded_grey": 236,
            "blood_red": 53,
            "forest_green": 23,
            "brown": 131,
            "gold": 221
        }
    

    def get_color(self, color: str) -> curses.color_pair:
        """Return color if supported"""
        color: str = color.strip().lower()
        color_pair_id: Optional[int] = self.supported_colors.get(color)

        if not color_pair_id:
            return curses.color_pair(0)  # Default white/black pair.
        return curses.color_pair(color_pair_id)

