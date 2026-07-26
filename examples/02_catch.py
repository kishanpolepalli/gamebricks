"""Catch the falling stars with your basket."""

from gamebricks import Game

game = Game(cells=8, title="Catch the stars")
hero = game.player(shape="basket", control="arrows", across=4, up=0)

game.hearts(2, every=10, move="falls")   # extra lives fall in like stars


@game.every(1)                        # every 1 second...
def drop():
    game.drop("star", move="falls", speed=3)


@game.when_touch(hero, "star")
def caught(star):
    game.score += 1
    star.burst()
    if game.score % 5 == 0:
        game.say(f"{game.score} stars!")


@game.when_missed("star")
def missed():
    game.lives -= 1


game.win_when(game.score_reaches(15))
game.start()

# TRY THIS
#   game.hearts(5, every=5)           -> a much kinder game
#   speed=8 in the drop line          -> much harder
#   game.every(0.4)                   -> a rain of stars
#   shape="ship" on the player line   -> a spaceship instead of a basket
