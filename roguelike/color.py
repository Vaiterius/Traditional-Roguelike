import curses
from typing import Optional


class Color:

    def __init__(self):
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        
        self.supported_colors = {
            "default": 1,
            "red": 2,
            "green": 3,
            "yellow": 4,
            "blue": 5,
            "magenta": 6,
            "cyan": 7,
            "white": 8
        }
    

    def get_color(self, color: str) -> curses.color_pair:
        color: str = color.strip().lower()
        color_pair_id: Optional[int] = self.supported_colors.get(color)
        if not color_pair_id:
            return curses.color_pair(0)  # Default white/black pair.
        return curses.color_pair(color_pair_id)

