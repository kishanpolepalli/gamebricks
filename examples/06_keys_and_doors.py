"""Two levels. Find the key, open the door, walk through it.

k is a key.  d is a door.  g is a ghost.
The door stays shut until you have the key. Win a level and the next
picture loads by itself — with your hearts topped back up.
"""

from gamebricks import Game

game = Game(cells=9, title="Find the key")
game.player(shape="hero", control="arrows")

game.levels(
    """
    #########
    #@..#..k#
    #.#.#.#.#
    #.#...#.#
    #.#####.#
    #...#..g#
    ###.#.###
    #d..#..c#
    #########
    """,
    """
    #########
    #@#...#k#
    #.#.#.#.#
    #...#..g#
    #####.###
    #k..#..c#
    #.#.#.#.#
    #.#...#d#
    #########
    """,
)

game.hearts(3, every=10)              # <-- and they refill on every level

game.start()

# TRY THIS
#   write a third level picture       -> add it inside game.levels(...)
#   game.legend(x="ghost")            -> now x in your picture means a ghost
#   game.hearts(1)                    -> one rescue per level, no more
