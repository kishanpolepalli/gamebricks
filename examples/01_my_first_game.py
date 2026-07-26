"""START HERE. A few lines and a coin you can move.

Change the two numbers on the coin line, save, run it again.
That is the whole game of making games.
"""

from gamebricks import Game

game = Game(cells=8)
game.show_grid()                      # so you can count the squares

hero = game.player(shape="hero", control="arrows", across=0, up=0)

game.coin(across=4, up=6)             # <-- CHANGE THESE TWO NUMBERS
game.coin(across=7, up=3)             # <-- and these

game.hearts(2)                        # 2 extra lives appear as you play

game.win_when(game.collected_all("coin"))
game.start()

# TRY THIS
#   game.hearts(6)                    -> hearts everywhere
#   game.hearts(0)                    -> none at all, be careful
#   game.ghost(across=7, up=7)        -> now you need those hearts
