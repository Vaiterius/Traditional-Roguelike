import cProfile
import pstats
import curses

from main import main

cProfile.run("curses.wrapper(main)", "tests/profiling/results")

with open("tests/profiling/results.txt", "w") as file:
    profile = pstats.Stats("tests/profiling/results", stream=file)
    profile.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()