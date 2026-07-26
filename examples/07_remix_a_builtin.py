"""Don't want to start from nothing? Load a finished game and change it."""

import gamebricks

game = gamebricks.load("platformer")     # a working game, not started yet

game.show_grid()                      # switch the counting grid on
game.coin(across=6, up=6)             # add your own coin
game.spike(across=4, up=1)            # and something to avoid
game.jump_power(4)                    # jump higher
game.hearts(5, every=5)               # be generous with extra lives
game.title("My remix")

game.start()

# Every ready-made game is built the same way, so the same lines work on
# all of them: catch, chase, maze, platformer, keys
#   gamebricks.play("chase")             -> play one straight away
#   gamebricks.load("chase")             -> get one to change first
