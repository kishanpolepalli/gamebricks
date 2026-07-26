"""Jump up the platforms and reach the flag. YOU design the level.

across = 0 is the far left.  up = 0 is the bottom row.
"""

from gamebricks import Game

game = Game(cells=8, title="Reach the flag")
game.player(shape="hero", control="arrows+jump", across=0, up=1)
game.show_grid()

game.ground()                                  # the floor
game.platform(across=2, up=2, width=2)         # <-- move these
game.platform(across=5, up=4, width=2)
game.platform(across=1, up=5, width=2)

game.coin(across=2, up=3)
game.coin(across=5, up=5)
game.flag(across=1, up=6)                      # <-- the finish

game.jump_power(3)                             # squares you can jump
game.hearts(2, every=12, up=1)                 # <-- hearts land on the floor

game.win_when(game.reached("flag"))
game.start()

# TRY THIS
#   jump_power(1)                     -> can you still reach the flag?
#   flag(across=7, up=7)              -> build a path up to it
#   game.spike(across=3, up=1)        -> something to jump over
#   game.hearts(4, every=6)           -> falling off costs less
