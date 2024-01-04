# Unnamed Roguelike

### 🚧 Under Development! 🚧

A retro traditional roguelike developed completely within the Python Standard Library and played on the terminal. Uses the curses library for terminal input/output handling. Fully ASCII interface and keyboard-controlled. Allows for saving ongoing games but once you die, there is no going back.

## Description

Equip yourself with diverse armor, face creatures head-on with formidable weapons, and unleash magical abilities as you descend into the monster-filled dungeon down a series of ever-more treacherous floors. Will you prove your mettle and conquer the hallowing depths, or will **darkness** claim you?

**Normal mode**: An ancient relic on the 27th floor needs to be retrieved. The room can only be revealed once a set of three other relics found throughout the previous floors are activated. Once retrieved, it must be taken back all the way up to the entrance to win the game. <br>
**Endless mode**: There is no need to activate or fetch anything. You are cursed to fight until you die!

### Development screenshots

<img alt="A screenshot of the main menu with a randomly-generated dungeon background" src="screenshots/title_screen.png" width="250">
<img alt="A screenshot of the menu to select ongoing savegames for continuing" src="screenshots/continue_game_screen.png" width="250">
<img alt="A screenshot of your character going through a dungeon floor" src="screenshots/gameplay.png" width="250">
<img alt="A screenshot of choosing an attribute to level up" src="screenshots/levelup.png" width="250">

## Run Me!

I will upload this game to [itch.io](https://vaiterius.itch.io/) as soon as it's finished. Every commit to this repo should be a working state of the game so you can run it anytime during its development process. Clone the repo into your machine and run the `main.py` file in the root directory.

Must have [Python](https://www.python.org/) 3.10+ installed.

**Linux users**: Should work natively. <br>
**Windows users**: Might not work natively, only the Linux distributions of Python has the curses module required to play the game as far as I know. You might need to install the module seperately [here](https://pypi.org/project/windows-curses/), preferrably in a virtual environment. <br>
**Mac users**: ¯\\_(ツ)_/¯

## Controls

### Movement
| Direction    | Arrow Keys   | Numpad Keys     | Vi Keys      |
|--------------|--------------|-----------------|--------------|
| Up           | <kbd>↑</kbd> | <kbd>↑</kbd>    | <kbd>k</kbd> |
| Down         | <kbd>↓</kbd> | <kbd>↓</kbd>    | <kbd>j</kbd> |
| Left         | <kbd>←</kbd> | <kbd>←</kbd>    | <kbd>h</kbd> |
| Right        | <kbd>→</kbd> | <kbd>→</kbd>    | <kbd>l</kbd> |
| Upper-left   |              | <kbd>Home</kbd> | <kbd>y</kbd> |
| Upper-right  |              | <kbd>PgUp</kbd> | <kbd>u</kbd> |
| Bottom-left  |              | <kbd>End</kbd>  | <kbd>b</kbd> |
| Bottom-right |              | <kbd>PgDn</kbd> | <kbd>n</kbd> |

*Note that the player can move diagonally but this is not supported with arrow keys*

### Actions

#### General

**Save and close game** - <kbd>Shift</kbd> + <kbd>q</kbd> <br>
**Save and go back to main menu** - <kbd>m</kbd> <br>
**Confirm action** - <kbd>Enter</kbd> <br>
**Go back to previous state/menu** - <kbd>Backspace</kbd>

#### In-Game

**Open inventory** - <kbd>Tab</kbd> or <kbd>i</kbd> <br>
**Pick up an item** - <kbd>p</kbd> <br>
**Drop an item from inventory** - <kbd>d</kbd> <br>
**Shoot arrow/staff projectile** - <kbd>Enter</kbd> <br>
**Select target** - See [movement](#movement) controls <br>
**Activate relic** - <kbd>Shift</kbd> + <kbd>Enter</kbd> <br>
**Descend stairs** - <kbd>></kbd> <br>
**Ascend stairs** - <kbd><</kbd> <br>
**Wait a turn** - <kbd>.</kbd> or <kbd>Del</kbd>


## Contributions
The game will be open to community feedback soon for any questions, feedback, bug reports, etc.

Stay tuned!