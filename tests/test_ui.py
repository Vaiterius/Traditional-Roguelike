import string
import curses
import random
from collections import namedtuple
from collections import deque  # O(1) insertion for message log


def main(stdscr):
    curses.curs_set(0)  # Do not display cursor.
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    # Map view config.
    map_height = 25
    map_width = 100
    grid = [
        ['.' if random.random() > 0.33 else ':' for x in range(map_width)]
        for y in range(map_height)
    ]
    grid_height = 20
    grid_width = 85
    center_box_width = 6  # Center thresholds for map scrolling.
    center_box_height = 2
    grid_window = curses.newwin(grid_height + 2, grid_width + 2, 0, 0)
    
    # Focal point (player).
    Player = namedtuple("player", "char, x, y")
    player = Player(char='@', x = grid_height // 2, y = grid_width // 2)
    
    # Message log config.
    msgs = deque([
        "This will be a very cool game!",
        "Welcome to my roguelike test!"
    ])
    msg_log_width = grid_width + 2
    msg_log_height = 10
    msg_window = curses.newwin(msg_log_height, msg_log_width, grid_height + 2, 0)
    
    # Sidebar config.
    sidebar_width = 28
    sidebar_height = grid_height + msg_log_height + 2
    sidebar = curses.newwin(sidebar_height, sidebar_width, 0, grid_width + 2)

    while True:
        grid_window.erase()
        msg_window.erase()
        sidebar.erase()
        
        # Display grid map.
        grid_window.border()
        grid_window.addstr(0, 2, "Gerard - Lv. 1")
        for x in range(grid_height):
            for y in range(grid_width):
        # for x in range(grid[player.x:], grid_height[player.x:]):
        #     for y in range(...):
                grid_window.addstr(x + 1, y + 1, grid[x][y])
        grid_window.addstr(player.x, player.y, player.char)
        
 
        # Display message log.
        msg_window.border()
        msg_window.addstr(0, 2, "MESSAGE LOG")
        # Most recent messages on the bottom of the log.
        cursor = 0
        for i in range(msg_log_height - 2, 0, -1):
            msg_window.addstr(i, 2, msgs[cursor])
            cursor += 1
            if cursor > len(msgs) - 1:
                break

        # Display sidebar.
        sidebar.border()
        
        key = stdscr.getkey()
        # WASD to move the map around.
        if key == 'w':
            ...
        elif key == 'a':
            ...
        elif key == 's':
            ...
        elif key == 'd':
            ...
        # '.' to append to message log.
        if key == '.':
            msgs.appendleft(''.join(random.choices(string.ascii_lowercase, k=msg_log_width - 3)))
            # msgs.appendleft("Hello hello hello hello hello hello hello hello hello hello hello hi!")
        
        grid_window.refresh()
        msg_window.refresh()
        sidebar.refresh()
        


curses.wrapper(main)
