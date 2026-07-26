"""The `gamebricks` command — play first, then get the code to change.

    gamebricks                     what you can do
    gamebricks maze                play a ready-made game
    gamebricks list                the five games
    gamebricks copy                copy the seven example files here, to edit
    gamebricks new my_game.py      start a blank game of your own

`python -m gamebricks ...` does exactly the same thing.
"""

import shutil
import sys
from pathlib import Path

from . import GAMES, play, __version__

FOLDER = "my-gamebricks-games"


def _examples_dir():
    """Where the example .py files live — inside the installed package, or
    in the repo when running from a checkout."""
    here = Path(__file__).resolve().parent
    for candidate in (here / "examples", here.parent.parent / "examples"):
        if candidate.is_dir():
            return candidate
    return None


def _help():
    print(f"\n  GameBricks {__version__} — build real games with a few lines "
          f"of Python\n")
    print("  PLAY ONE NOW")
    for name in GAMES:
        print(f"      gamebricks {name}")
    print("\n  GET SEVEN GAMES YOU CAN CHANGE")
    print(f"      gamebricks copy          puts them in ./{FOLDER}/")
    print(f"      python {FOLDER}/01_my_first_game.py")
    print("\n  OR START A BLANK ONE OF YOUR OWN")
    print("      gamebricks new my_game.py")
    print("      python my_game.py\n")


def _copy(dest_name=FOLDER):
    src = _examples_dir()
    if src is None:
        print("I couldn't find my example files. Try reinstalling GameBricks:")
        print("    pip install --force-reinstall gamebricks")
        return 1
    dest = Path.cwd() / dest_name
    dest.mkdir(exist_ok=True)
    copied = []
    for f in sorted(src.glob("*.py")):
        target = dest / f.name
        if target.exists():
            print(f"  already here, left alone:  {dest_name}/{f.name}")
            continue
        shutil.copyfile(f, target)
        copied.append(f.name)
    if copied:
        print(f"\n  Copied {len(copied)} games into ./{dest_name}/\n")
        for name in copied:
            print(f"      {name}")
    print("\n  Start with the first one:")
    print(f"      python {dest_name}/01_my_first_game.py")
    print("\n  Open it in any editor, change a number, run it again.\n")
    return 0


STARTER = '''"""My game. Change the numbers, save, run it again.

    across = 0  is the far LEFT       up = 0  is the BOTTOM
    While playing:  R restart  P pause  G grid  M mute  Esc quit
"""

from gamebricks import Game

game = Game(cells=8, title="My game")
game.show_grid()                      # so you can count the squares

hero = game.player(shape="hero", control="arrows", across=0, up=0)

# ---- put your things on the grid -------------------------------------
game.coin(across=4, up=6)             # <-- CHANGE THESE NUMBERS
game.coin(across=7, up=3)
# game.ghost(across=7, up=7)          # <-- take the # away to wake it up
# game.wall(across=3, up=3, width=2)

game.hearts(2)                        # extra lives that appear as you play


# ---- your rules ------------------------------------------------------
@game.when_touch(hero, "coin")
def grab(coin):
    game.score += 1
    hero.say("got it!")
    coin.burst()


# ---- how you win -----------------------------------------------------
game.win_when(game.collected_all("coin"))

game.start()
'''


def _new(filename="my_game.py"):
    """Write one blank-slate game a kid can build on."""
    if not filename.endswith(".py"):
        filename += ".py"
    target = Path.cwd() / filename
    if target.exists():
        print(f"\n  {filename} already exists — I won't overwrite your work.")
        print("  Pick another name:  gamebricks new my_second_game.py\n")
        return 1
    target.write_text(STARTER, encoding="utf-8")
    print(f"\n  Made {filename} — a small game with room to grow.\n")
    print(f"      python {filename}\n")
    print("  Open it in any editor, change a number, run it again.\n")
    return 0


def _first_run_hint():
    """If they haven't copied the games out yet, that's the next thing to do."""
    if (Path.cwd() / FOLDER).is_dir():
        return
    print("  ┌────────────────────────────────────────────────────────┐")
    print("  │  New here? Run this to get the games you can change:   │")
    print("  │                                                        │")
    print("  │      gamebricks copy                                   │")
    print("  └────────────────────────────────────────────────────────┘\n")


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        _help()
        _first_run_hint()
        return 0

    cmd = args[0]

    if cmd in ("-V", "--version", "version"):
        print(f"gamebricks {__version__}")
        return 0

    if cmd in ("list", "games"):
        for name in GAMES:
            print(name)
        return 0

    if cmd in ("copy", "examples", "get"):
        return _copy(args[1] if len(args) > 1 else FOLDER)

    if cmd in ("new", "start"):
        return _new(args[1] if len(args) > 1 else "my_game.py")

    if cmd in GAMES:
        play(cmd)
        print(f"\n  Want to change that game? Get the code:\n")
        print(f"      gamebricks copy\n")
        return 0

    print(f"\n  I don't know the game '{cmd}'.")
    print(f"  Try one of these: {', '.join(GAMES)}")
    print("  Or run 'gamebricks' on its own to see everything.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
