import string
import curses
import random
from collections import namedtuple
from collections import deque  # O(1) insertion for message log


def from_inventory(inventory_window: curses.newwin, msgs: deque):
    x, y = inventory_window.getmaxyx()
    inventory_window.refresh()
    
    INVENTORY = "INVENTORY"
    
    inventory_items = ["item 1", "item 2", "item 3"]
    num_showable_items = x - 2  # account border cells
    
    vertical_cursor_pos = 1  # make sure this matches with the item index

    inventory_window.keypad(True)

    while True:
        inventory_window.erase()
        
        inventory_window.border()
        inventory_window.addstr(0, (y // 2) - (len(INVENTORY) // 2), "INVENTORY")
        inventory_window.addstr(vertical_cursor_pos, 2, ">")
        
        # Show inventory items.
        iter_cursor = 1
        for item in inventory_items:
            inventory_window.addstr(iter_cursor, 4, str(iter_cursor) + ") " + item)
            iter_cursor += 1
        
        key = inventory_window.getkey()
        if key == "m":
            return ""
        if key == "KEY_UP":
            vertical_cursor_pos -= 1
        elif key == "KEY_DOWN":
            vertical_cursor_pos += 1
        elif key == "KEY_ENTER" or key == "\n":
            return inventory_items[vertical_cursor_pos - 1]

        # recalculate valid cursor positions
        vertical_cursor_pos = max(1, min(vertical_cursor_pos, min(num_showable_items, len(inventory_items))))

        inventory_window.refresh()


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


    # CALCULATE GAME WINDOW
    game_height = grid_height + 2 + msg_log_height
    game_width = msg_log_width + sidebar_width
    game_view_test_window = curses.newwin(game_height, game_width, 0, 0)

    # INVENTORY
    inventory_height = 15
    inventory_width = 40
    inventory_origin_x = (game_height // 2) - (inventory_height // 2)
    inventory_origin_y = (game_width // 2) - (inventory_width // 2)
    inventory_window = curses.newwin(inventory_height, inventory_width, inventory_origin_x, inventory_origin_y)


    stdscr.refresh()
    grid_window.refresh()
    msg_window.refresh()
    sidebar.refresh()
    
    # game_view_test_window.refresh()

    while True:
        grid_window.erase()
        msg_window.erase()
        sidebar.erase()
        # game_view_test_window.erase()
        
        # Display grid map.
        grid_window.border()
        grid_window.addstr(0, 2, "Gerard - Lv. 1")
        for x in range(grid_height):
            for y in range(grid_width):
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
        
        # Menu
        if key == "m":
            action = from_inventory(inventory_window, msgs)
            if action is not "":
                msgs.appendleft(action)
                
        # game_view_test_window.border()
        
        grid_window.refresh()
        msg_window.refresh()
        sidebar.refresh()
        # game_view_test_window.refresh()
        


curses.wrapper(main)
