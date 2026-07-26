"""Draw your own maze with your keyboard, then collect every coin.

# is a wall.  . is empty space.  @ is you.  c is a coin.  g is a ghost.
Redraw the picture however you like — just keep it square.
"""

from gamebricks import Game

game = Game(cells=9, title="Collect the coins")
game.player(shape="hero", control="arrows")

game.level("""
    #########
    #@..#..c#
    #.#.#.#.#
    #.#...#.#
    #.###.#g#
    #c..#.#.#
    ##.##.#.#
    #..c..#c#
    #########
""")

game.hearts(2, every=12)              # <-- extra lives, now and then

game.win_when(game.collected_all("coin"))
game.start()

# TRY THIS
#   add another g                     -> two ghosts hunting you
#   game.hearts(4, every=6)           -> more rescues
#   knock a wall out (# -> .)         -> a shortcut
