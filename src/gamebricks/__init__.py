"""
gamebricks — build real games with a few lines of Python.

Play something in one line:

    import gamebricks
    gamebricks.play("maze")

Or make it yours. Everything sits on a grid, and everything uses the same two
numbers: `across` (0 = far left) and `up` (0 = bottom).

    from gamebricks import Game

    game = Game(cells=8)
    hero = game.player(shape="hero", control="arrows", across=0, up=0)

    game.coin(across=3, up=5)
    game.coin(across=6, up=2)
    game.ghost(across=7, up=7)
    game.show_grid()

    @game.when_touch(hero, "coin")
    def grab(coin):
        game.score += 1
        coin.burst()

    game.win_when(game.collected_all("coin"))
    game.start()

Change a number. Run it again. That is the whole loop — and it is why the
learning sticks: the code has visible consequences you can play.

The kid's code never changes if the engine underneath changes. Today it runs
on a desktop window (pygame); tomorrow the same code can run in a browser.
"""

from .game import Game
from .builtin import load, play, GAMES
from .errors import GameError
from .model import SHAPES, CONTROLS, MOVES

__all__ = ["Game", "load", "play", "GAMES", "GameError",
           "SHAPES", "CONTROLS", "MOVES"]
__version__ = "0.3.0"
