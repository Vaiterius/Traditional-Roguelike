import math
import curses

def main(stdscr):
    # Turn off cursor blinking
    curses.curs_set(0)
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # Clear screen
    stdscr.clear()

    bar_width = 100
    
    stdscr.addstr(0, 0, "Bar at 100%")
    output_to_screen(stdscr, 1, 0, get_bar_from_percent(1.00, bar_width), bar_width)
    
    stdscr.addstr(2, 0, "Bar at 80%")
    output_to_screen(stdscr, 3, 0, get_bar_from_percent(0.80, bar_width), bar_width)
    
    stdscr.addstr(4, 0, "Bar at 75%")
    output_to_screen(stdscr, 5, 0, get_bar_from_percent(0.75, bar_width), bar_width)
    
    stdscr.addstr(6, 0, "Bar at 50%")
    output_to_screen(stdscr, 7, 0, get_bar_from_percent(0.50, bar_width), bar_width)
    
    stdscr.addstr(8, 0, "Bar at 25%")
    output_to_screen(stdscr, 9, 0, get_bar_from_percent(0.25, bar_width), bar_width)
    
    stdscr.addstr(10, 0, "Bar at 10%")
    output_to_screen(stdscr, 11, 0, get_bar_from_percent(0.10, bar_width), bar_width)
    
    stdscr.addstr(12, 0, "Bar at 5%")
    output_to_screen(stdscr, 13, 0, get_bar_from_percent(0.05, bar_width), bar_width)
    
    stdscr.addstr(14, 0, "Bar at 0%")
    output_to_screen(stdscr, 15, 0, get_bar_from_percent(0.00, bar_width), bar_width)

    # Refresh screen
    stdscr.refresh()

    # Wait for user input
    stdscr.getch()


def output_to_screen(stdscr, start_row: int, start_col: int, bar: str, bar_width: int):
    stdscr.addstr(start_row, start_col, bar, curses.color_pair(3))
    rest = bar_width - len(bar)
    for _ in range(rest):
        stdscr.addstr('░', curses.color_pair(2))


def get_bar_from_percent(percent: float, bar_width: int) -> None:
    assert(percent <= 1.00)
    assert(percent >= 0.00)

    FULL_DENSITY_BLOCK = '█'
    HIGH_DENSITY_BLOCK = '▓'
    MED_DENSITY_BLOCK = '▒'
    LOW_DENSITY_BLOCK = '░'

    bar = ""
    num_blocks = math.ceil(percent * bar_width)
    for _ in range(num_blocks):
        bar += FULL_DENSITY_BLOCK
    
    return bar

# BAR_WIDTH = 10
# print("100% for reference:")
# print("▓▓▓▓▓▓▓▓▓▓\n")
# print(get_bar_from_percent(1.00, BAR_WIDTH))
# print(get_bar_from_percent(0.75, BAR_WIDTH))
# print(get_bar_from_percent(0.50, BAR_WIDTH))
# print(get_bar_from_percent(0.25, BAR_WIDTH))
# print(get_bar_from_percent(0.00, BAR_WIDTH))


# Call the main function
curses.wrapper(main)