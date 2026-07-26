"""Dodge the ghosts. Survive 20 seconds to win.

Hearts keep appearing in empty squares while you play, so a bad bump
isn't the end. YOU decide how many turn up.
"""

from gamebricks import Game

game = Game(cells=8, title="Dodge the ghosts")
hero = game.player(shape="hero", control="arrows", across=4, up=4)

game.border()                         # a wall around the edge
game.ghost(across=1, up=6)            # <-- move the ghosts around
game.ghost(across=6, up=6)

game.hearts(3, every=7)               # <-- 3 extra lives, one every 7 seconds


@game.every(5)
def more_ghosts():
    game.ghost(across=1, up=1, speed=3)


@game.when_touch(hero, "ghost")
def caught(ghost):
    game.lives -= 1
    hero.say("ouch!")
    ghost.burst()


@game.when_touch(hero, "heart")
def rescued(heart):
    game.lives += 1
    hero.say("thank you!")
    heart.burst()


game.win_when(game.survived(20))
game.start()

# TRY THIS
#   game.hearts(8, every=3)           -> hearts raining in, easy mode
#   game.hearts(0)                    -> no rescues, three lives only
#   speed=1 on a ghost                -> a slow, sleepy ghost
#   move="bounces" instead of chases  -> it ignores you and pings about
