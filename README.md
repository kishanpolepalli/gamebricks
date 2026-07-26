<div align="center">

# 🧱 GameBricks

**Build real games with a few lines of Python.**

[![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ages](https://img.shields.io/badge/ages-9–14-F2B705?style=for-the-badge)](#-what-youll-learn)
[![Games](https://img.shields.io/badge/games-5_ready_to_play-2F8F63?style=for-the-badge)](#-the-examples-in-the-order-to-try-them)
[![Tests](https://img.shields.io/badge/tests-headless-7B5BD6?style=for-the-badge)](#-tests)
[![License](https://img.shields.io/badge/license-MIT-16192E?style=for-the-badge)](#-license)

_Every genre is the same six bricks with different settings._

</div>

---

## ⚡ Sixty seconds to your first game

```bash
pip install gamebricks
gamebricks                         # what you can do
gamebricks maze                    # play one right now
gamebricks copy                    # 7 example games -> ./my-gamebricks-games/
python my-gamebricks-games/01_my_first_game.py

gamebricks new my_game.py          # or start a blank one of your own
python my_game.py
```

Nothing is downloaded — the example files ship **inside** the package, and
`gamebricks copy` writes them into the kid's own folder as real, editable
files. It never overwrites a file that's already there, so their edits are safe
if they run it twice. `gamebricks new` writes a single small game with
`# <-- CHANGE THESE NUMBERS` markers, for a kid who'd rather start from almost
nothing. `python -m gamebricks ...` does the same as `gamebricks ...` if the
command isn't on the PATH.

> **Not on PyPI yet.** Until it is, install from the folder with
> `pip install -e ".[dev]"`, or skip installing entirely with
> `PYTHONPATH=src python3 examples/02_catch.py`.

Then make it yours:

```python
import gamebricks

game = gamebricks.load("maze")     # a finished game...
game.coin(across=6, up=6)          # ...with your coin added
game.hearts(4)                     # ...and four extra lives
game.show_grid()
game.start()
```

Needs Python 3.12+. One dependency (pygame) draws the window.

---

## 🎯 The one idea: `across` and `up`

Everything sits on a grid, and **everything uses the same two numbers**:

```
across = 0   is the far LEFT column
up     = 0   is the BOTTOM row
```

Like a graph in maths class. Turn the grid on with `game.show_grid()` and the
numbers are printed on the screen, so a kid can count squares with a finger and
type what they counted.

```python
game.coin(across=3, up=5)
game.ghost(across=7, up=7)
game.platform(across=2, up=2, width=3)
game.flag(across=1, up=6)
game.ground()                        # floor across the bottom
game.border()                        # wall around the edge
game.row("coin", up=4)               # a whole line of them
```

**Change a number. Run it again. See it move.** That loop _is_ the product.

---

## 🕹️ A whole game

```python
from gamebricks import Game

game = Game(cells=8)
hero = game.player(shape="basket", control="arrows", across=4, up=0)

game.hearts(2, move="falls")             # extra lives drop in too

@game.every(1)
def drop():
    game.drop("star", move="falls")

@game.when_touch(hero, "star")
def caught(star):
    game.score += 1
    star.burst()

@game.when_missed("star")
def missed():
    game.lives -= 1

game.win_when(game.score_reaches(15))
game.start()
```

While it runs: <kbd>R</kbd> restart · <kbd>P</kbd> pause · <kbd>G</kbd> grid ·
<kbd>M</kbd> mute · <kbd>Esc</kbd> quit

---

## 🎨 Draw a level with your keyboard

One character per grid square. What you draw is what you see — right way up.

```python
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
```

|          |           |              |          |           |           |
| :------: | :-------: | :----------: | :------: | :-------: | :-------: |
| `#` wall | `.` empty |   `@` you    | `c` coin |  `k` key  | `d` door  |
| `*` star | `g` ghost | `=` platform | `F` flag | `H` heart | `^` spike |

Teach it a new character with `game.legend(x="ghost")`. Several pictures in a
row become levels — win one and the next loads itself:

```python
game.levels(level_one, level_two, level_three)
```

---

## ❤️ Extra lives, and how many

Hearts appear **while you play**, in a random empty square — never inside a
wall. The kid decides how generous the game is:

```python
game.hearts(3)                       # 3 extra lives, one every 8 seconds
game.hearts(6, every=4)              # six of them, twice as often
game.hearts(0)                       # none at all — three lives is all you get
game.hearts(2, move="falls")         # they drop in from the top
game.hearts(2, up=1)                 # always row 1, so they land on the floor
```

The budget refills on every new level and on restart. `game.free_square()` and
`game.is_free(across, up)` are public, so a kid can place anything fairly:

```python
spot = game.free_square()
game.coin(across=spot[0], up=spot[1])
```

---

## 🔑 Keys and doors

Placing a `k` and a `d` is enough. The door stays shut, tells you how many keys
it still wants, and swings open when you have them. Walk through it to finish
the level.

Every artifact has a **sensible default**, so something happens the moment a kid
places it:

| Place this        | And this happens, with no rule written               |
| ----------------- | ---------------------------------------------------- |
| `coin` / `star`   | score goes up, it bursts into sparkles               |
| `heart`           | you gain a life                                      |
| `spike` / `ghost` | you lose a life                                      |
| `key`             | you collect it, and it opens any door that wanted it |
| `door`            | walk through an open one to finish the level         |
| `flag`            | you win                                              |

Write your own `@game.when_touch` rule for that name and yours takes over.

---

## 🧩 Every game works the same way

Learning the second game should be almost free. So all five ready-made games —
and all seven examples — are written in the same order, with the same promises:

```
1  Game(cells=..., title=...)      the board
2  game.player(...)                who you are
3  the level                       walls, platforms, coins, the goal
4  game.hearts(n)                  extra lives that appear as you play
5  the rules                       @every, @when_touch, @when_missed
6  game.win_when(...)              one clear way to win
```

| Game          | How you win                | How you lose a life    | Hearts          |
| ------------- | -------------------------- | ---------------------- | --------------- |
| 🌟 catch      | `score_reaches(15)`        | miss a star            | 2, falling      |
| 👻 chase      | `survived(20)`             | a ghost touches you    | 3               |
| 🪙 maze       | `collected_all("coin")`    | a ghost hunts you      | 2               |
| 🚩 platformer | `reached("flag")`          | fall off the platforms | 2, on the floor |
| 🔑 keys       | walk through the last door | a ghost touches you    | 3 per level     |

Every game starts with 3 lives, every game can be lost, every game has exactly
one win rule on its own line, and <kbd>R</kbd> <kbd>P</kbd> <kbd>G</kbd>
<kbd>M</kbd> do the same thing in all of them. **The test suite enforces this** —
a new game with no `hearts()` line, or no way to lose, fails `pytest`.

---

## 🎓 What you'll learn

Not "concepts covered." These are the lines a kid actually types.

### Python, specifically

| They type                          | They're learning                          | The real name                  |
| ---------------------------------- | ----------------------------------------- | ------------------------------ |
| `game.coin(across=3, up=5)`        | giving a command with settings            | keyword arguments              |
| `speed = 3`                        | naming a value                            | a variable                     |
| `game.score += 1`                  | a number that changes                     | mutable state                  |
| `@game.every(1)`                   | doing something repeatedly                | a loop                         |
| `@game.when_touch(...)`            | a rule for when things collide            | a condition, an event handler  |
| `def caught(star):`                | a reusable instruction that takes a thing | a function with a parameter    |
| `star.burst()`                     | asking a thing to do something            | objects, methods, dot notation |
| `if game.score % 5 == 0:`          | making a decision                         | an `if`, modulo                |
| `game.say(f"{game.score} stars!")` | putting a number inside words             | an f-string                    |
| reading the error, fixing the line | that mistakes are information             | debugging                      |

### Maths, without calling it maths

- **Cartesian coordinates.** `across`/`up` with the origin at bottom-left _is_ a
  graph. They'll meet it in class later and already own it.
- **Zero-based counting.** Genuinely hard at nine — `show_grid()` makes it
  concrete instead of abstract.
- **2D grids.** The level picture is a hand-authored two-dimensional array.
- **Rates and estimation.** "One heart every 7 seconds." "Can I jump 3 squares
  to reach `up=6`?"

### Computational thinking

- **Decomposition** — every game is the same six bricks with different settings.
- **The build–test–fix loop.** Put the flag out of reach and _nothing errors_.
  They play, discover it's impossible, and fix it. That's debugging, and it's the
  most valuable habit in here.
- **Cause and effect through parameters** — `speed=8` vs `speed=3`,
  `hearts(0)` vs `hearts(6)`. Game balance is really hypothesis testing.
- **Abstraction** — noticing that `move="falls"` → `move="chases"` turns a
  catching game into a chasing game.

### And the part that decides whether they continue

Authorship — it's _their_ level, not a worksheet. Tolerance for failure, because
failure is playable rather than punitive. And the first time they hand a level to
a sibling and watch them fail: that's empathy plus specification.

### 🚧 Honest gaps

It does **not** teach data structures beyond lists, writing their own classes
(they _use_ objects, they don't define them), file I/O, algorithms, recursion,
testing, or version control. That's fine — this is the on-ramp. The natural next
step is a kid outgrowing `hearts()` and writing their own spawn logic with
`free_square()`, which is where lists, loops and conditions stop being
decorative.

📄 See **`Teacher Sheet`** for a one-page map of each example to the concept it
introduces, and **`GameBricks Cheat Sheet`** for the printable kid-facing poster.

---

## 🎛️ The dials you can turn

```
GRID      Game(cells=8)  ·  game.show_grid()  ·  game.title("...")
CONTROL   arrows · wasd · mouse · arrows+jump
MOVE      still · falls · falls_fast · drifts · chases · bounces
SHAPES    hero basket ship star coin ghost wall platform
          flag block heart key door spike
LIVES     game.hearts(count, every=8, move="still", up=None)
ON TOUCH  score += 1 · lives -= 1 · remove() · burst() · say("hi") · grow()
GOAL      score_reaches(n) · survived(s) · collected_all("coin") · reached("flag")
```

Mix them freely. That's every game.

---

## 📚 The examples, in the order to try them

|     | File                    | What's new in it                          |
| --- | ----------------------- | ----------------------------------------- |
| 1   | `01_my_first_game.py`   | a few lines, and a coin to move           |
| 2   | `02_catch.py`           | falling stars, a timer loop, losing lives |
| 3   | `03_chase.py`           | things that hunt you, your own heart rule |
| 4   | `04_maze.py`            | a maze you draw as text                   |
| 5   | `05_platformer.py`      | gravity, jumping, a level you design      |
| 6   | `06_keys_and_doors.py`  | keys, locked doors, two levels            |
| 7   | `07_remix_a_builtin.py` | start from a finished game and change it  |

Every one ends with a `# TRY THIS` list — three tiny edits, each with a visible
consequence.

---

## 💬 Friendly errors that teach

No scary red tracebacks. Every mistake is a tiny lesson with the fix included:

```
Oops — I don't know the shape 'basktet'.
Try one of these: hero, basket, ship, star, coin, ghost, ...
(did you mean 'basket'?)
```

```
You asked me to put something at across=99, up=2,
but this grid only goes from 0 to 7 in both directions.
Pick smaller numbers — or make the grid bigger with Game(cells=100).
```

```
In your level picture I found the character 'z',
but I don't know what to build for it.
You can teach me a new one:  game.legend(z="ghost")
```

---

## 🏗️ Built to grow

The kid's code never changes if the engine underneath does.

```
model.py             the whole game as pure state — zero rendering code
game.py              the one object a kid touches
level.py             text-art levels
builtin.py           the five ready-made games, written in kid-facing code
errors.py            every mistake as a friendly lesson
renderer_pygame.py   the ONLY file that imports pygame
sounds.py            beeps generated as maths — no audio files to ship
```

Today GameBricks runs in a desktop window; because the model is renderer-free,
the same game code is designed to run in a browser later — so a kid's game could
one day be shared by a link.

---

## ✅ Tests

```bash
pip install -e ".[dev]"
pytest
```

The suite is **headless** — it never opens a window, because everything worth
testing lives in the pygame-free model. It covers the grid maths, level parsing,
the friendly errors, the heart budget, and the cross-game contract.

---

## 📄 License

MIT. Made for kids, teachers, and anyone who wants their first program to be
something they can _play_.

[GitHub Repository](https://github.com/kishanpolepalli/gamebricks)
