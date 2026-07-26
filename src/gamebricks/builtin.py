"""Ready-made games: one line to play, then change the numbers.

    import gamebricks

    gamebricks.play("maze")            # play it right now

    game = gamebricks.load("maze")     # or take it and make it yours
    game.coin(across=6, up=6)       # add a coin where YOU want it
    game.hearts(5)                  # five extra lives, not two
    game.show_grid()                # switch the counting grid on
    game.start()

EVERY game in here is built the same way, in the same order, so that moving
from one to the next feels familiar instead of new:

    1  Game(cells=..., title=...)      the board
    2  game.player(...)                who you are
    3  the level                       walls, platforms, coins, the goal
    4  game.hearts(n)                  extra lives that appear as you play
    5  the rules                       @every, @when_touch, @when_missed
    6  game.win_when(...)              one clear way to win

And every game keeps the same promises:

    * you start with 3 lives and you can always lose one
    * extra lives appear during play, and `game.hearts(n)` sets how many
    * there is exactly one win rule, written on its own line
    * R restarts, P pauses, G shows the grid, M mutes

Nothing here is magic — it is all the same commands a kid types, so opening
this file is a fair way to learn.
"""

from . import errors
from .game import Game

GAMES = ("catch", "chase", "maze", "platformer", "keys")


def load(name="catch"):
    """Build a ready-made game and hand it back, unstarted, to customise."""
    if name not in GAMES:
        raise errors.unknown("game", name, GAMES)
    return globals()[f"_{name}"]()


def play(name="catch"):
    """Build a ready-made game and start it immediately."""
    load(name).start()


# ---------------------------------------------------------------- catch ----
def _catch():
    game = Game(cells=8, title="Catch the stars")
    hero = game.player(shape="basket", control="arrows", across=4, up=0)

    game.hearts(2, every=10, move="falls")     # extra lives drop in too

    @game.every(1)
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
    return game


# ---------------------------------------------------------------- chase ----
def _chase():
    game = Game(cells=8, title="Dodge the ghosts")
    hero = game.player(shape="hero", control="arrows", across=4, up=4)

    game.border()
    game.ghost(across=1, up=6)
    game.ghost(across=6, up=6)

    game.hearts(3, every=7)                    # a rescue every 7 seconds

    @game.every(5)
    def more_ghosts():
        game.ghost(across=1, up=1, speed=3)

    @game.when_touch(hero, "ghost")
    def caught(ghost):
        game.lives -= 1
        hero.say("ouch!")
        ghost.burst()

    game.win_when(game.survived(20))
    return game


# ----------------------------------------------------------------- maze ----
def _maze():
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

    game.hearts(2, every=12)                   # rare, the maze is calm

    game.win_when(game.collected_all("coin"))
    return game


# ------------------------------------------------------------ platformer ---
def _platformer():
    game = Game(cells=8, title="Reach the flag")
    game.player(shape="hero", control="arrows+jump", across=0, up=1)

    game.ground()
    game.platform(across=2, up=2, width=2)
    game.platform(across=5, up=4, width=2)
    game.platform(across=1, up=5, width=2)
    game.coin(across=2, up=3)
    game.coin(across=5, up=5)
    game.flag(across=1, up=6)
    game.jump_power(3)

    game.hearts(2, every=12, up=1)             # on the floor, walk into them

    game.win_when(game.reached("flag"))
    return game


# ----------------------------------------------------------- keys & doors --
def _keys():
    game = Game(cells=9, title="Find the key, open the door")
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

    game.hearts(3, every=10)

    # the door finishes a level all by itself; the last door wins the game
    return game
