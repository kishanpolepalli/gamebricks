"""The Game — the one object a kid touches. Reads like plain English.

Everything a kid places uses the SAME two numbers:

    across = 0   far left column
    up     = 0   bottom row

    game.coin(across=3, up=5)
    game.wall(across=0, up=0, width=8)
    game.place("ghost", across=7, up=7, move="chases")

Change a number, run it again, see it move. That is the whole loop.
"""

import random

from . import errors, level as level_art
from .model import World, Thing, SHAPES, CONTROLS, MOVES

# How big each shape is, as a fraction of one grid square.
_SIZES = {
    "wall": (1.0, 1.0),
    "block": (1.0, 1.0),
    "platform": (1.0, 0.35),
    "spike": (1.0, 0.4),
    "door": (0.8, 1.0),
    "flag": (0.6, 0.95),
    "coin": (0.45, 0.45),
    "key": (0.5, 0.4),
    "star": (0.55, 0.55),
    "heart": (0.5, 0.45),
    "ghost": (0.6, 0.6),
    "hero": (0.6, 0.6),
    "basket": (0.85, 0.5),
    "ship": (0.7, 0.6),
}
_DEFAULT_SIZE = (0.6, 0.6)


class Game:
    """A game a kid builds. They describe what they want; we handle how."""

    def __init__(self, cells=8, size=640, title="My GameBricks Game",
                 width=None, height=None):
        if cells < 3:
            raise errors.GameError(
                "A grid needs at least 3 squares across.\nTry: Game(cells=8)")
        w = width or size
        h = height or size
        self.world = World(w, h, cells=cells)
        self.world.title = title
        self._spawners = []        # [interval, fn, accumulated]
        self._touch_rules = []     # (thing_or_PLAYER, name, fn)
        self._miss_rules = {}      # name -> fn
        self._win_check = None
        self._level_texts = []
        self._level_index = 0
        self._legend = {}
        self._player_cfg = None
        self._start_time = None
        self._heart_plan = None      # (count, every, move, up)
        self._heart_budget = 0

    # ---- the grid --------------------------------------------------------
    @property
    def cells(self):
        """How many squares across (and up). Set with Game(cells=...)."""
        return self.world.cells

    @property
    def cell(self):
        """Size of one grid square in pixels. Kids rarely need this."""
        return self.world.cell

    def show_grid(self, on=True):
        """Draw faint grid lines and numbers so you can count squares."""
        self.world.show_grid = on
        return self

    def sound(self, on=True):
        self.world.sound_on = on
        return self

    def title(self, text):
        self.world.title = str(text)
        return self

    # ---- score / lives / keys are plain attributes ------------------------
    @property
    def score(self):
        return self.world.score

    @score.setter
    def score(self, v):
        self.world.score = v

    @property
    def lives(self):
        return self.world.lives

    @lives.setter
    def lives(self, v):
        self.world.lives = v

    @property
    def keys(self):
        return self.world.keys

    @keys.setter
    def keys(self, v):
        self.world.keys = v

    # ---- BLOCK 1: the player ---------------------------------------------
    def player(self, shape="hero", control="arrows", across=None, up=None):
        if shape not in SHAPES:
            raise errors.unknown("shape", shape, SHAPES)
        if control not in CONTROLS:
            raise errors.unknown("control", control, CONTROLS)
        w = self.world
        if w.player is not None:          # a second player() replaces the first
            w.things = [t for t in w.things if t is not w.player]
        self._player_cfg = dict(shape=shape, control=control,
                                across=across, up=up)
        if across is None:
            across = w.cells // 2
        if up is None:
            up = 0
        p = self._make(shape, across, up, name="player")
        w.player = p
        w.control = control
        w.gravity_on = control == "arrows+jump"
        return p

    # ---- BLOCK 2: put a thing on the grid --------------------------------
    def place(self, name, across=0, up=0, move="still", shape=None,
              speed=3, width=1, height=1):
        """The one placement command. Everything else is a shortcut for it."""
        if move not in MOVES:
            raise errors.unknown("move", move, MOVES)
        if name not in SHAPES and shape is None:
            raise errors.unknown("shape", name, SHAPES)
        self._check_grid(across, up)
        return self._make(name, across, up, name=name, move=move, shape=shape,
                          speed=speed, cells_w=width, cells_h=height)

    # friendly shortcuts — same numbers, shorter lines
    def coin(self, across, up):
        return self.place("coin", across, up)

    def star(self, across, up, move="still"):
        return self.place("star", across, up, move=move)

    def key(self, across, up):
        return self.place("key", across, up)

    def door(self, across, up, needs=1):
        d = self.place("door", across, up)
        d.needs = needs
        return d

    def flag(self, across, up):
        return self.place("flag", across, up)

    def heart(self, across, up):
        return self.place("heart", across, up)

    def ghost(self, across, up, move="chases", speed=3):
        return self.place("ghost", across, up, move=move, speed=speed)

    def wall(self, across, up, width=1, height=1):
        return self.place("wall", across, up, width=width, height=height)

    def block(self, across, up, width=1, height=1):
        return self.place("block", across, up, width=width, height=height)

    def platform(self, across, up, width=3):
        return self.place("platform", across, up, width=width)

    def spike(self, across, up, width=1):
        return self.place("spike", across, up, width=width)

    def ground(self):
        """A floor across the whole bottom row."""
        return self.place("platform", 0, 0, width=self.cells, height=1)

    def border(self, thickness=1):
        """A wall all the way around the edge, so nothing escapes."""
        n = self.cells
        made = []
        for i in range(n):
            for t in range(thickness):
                made.append(self.wall(i, t))
                made.append(self.wall(i, n - 1 - t))
                made.append(self.wall(t, i))
                made.append(self.wall(n - 1 - t, i))
        return made

    def row(self, name, up, from_across=0, to_across=None, step=1):
        """A whole line of the same thing: game.row("coin", up=5)."""
        end = self.cells - 1 if to_across is None else to_across
        return [self.place(name, a, up)
                for a in range(from_across, end + 1, step)]

    # ---- BLOCK 3: things that appear while you play -----------------------
    def drop(self, name, across=None, move="falls", speed=3, shape=None):
        """Send something falling in from the top of one column."""
        if across is None:
            across = random.randint(0, self.cells - 1)
        t = self._make(name, across, self.cells, name=name, move=move,
                       shape=shape, speed=speed)
        return t

    def spawn(self, name, move="falls", speed=3, shape=None,
              across=None, up=None):
        """Place a thing, or drop it in if it falls and you gave no square."""
        if move not in MOVES:
            raise errors.unknown("move", move, MOVES)
        if move in ("falls", "falls_fast") and up is None:
            return self.drop(name, across=across, move=move, speed=speed,
                             shape=shape)
        if across is None:
            across = random.randint(0, self.cells - 1)
        if up is None:
            up = random.randint(1, self.cells - 1)
        return self.place(name, across, up, move=move, shape=shape, speed=speed)

    def spawn_many(self, name, count=8, move="still", shape=None):
        return [self.spawn(name, move=move, shape=shape) for _ in range(count)]

    # ---- BLOCK 4: draw a whole level as a picture -------------------------
    def legend(self, **marks):
        """Teach the level picture a new character: game.legend(x="ghost")."""
        for ch, name in marks.items():
            if name not in SHAPES and name != "player":
                raise errors.unknown("shape", name, SHAPES)
            self._legend[ch] = name
        return self

    def level(self, text):
        """Build a level from text art. See gamebricks/level.py for the legend."""
        placements, cols, rows = level_art.parse(text, self._legend)
        if cols > self.cells or rows > self.cells:
            self._resize(max(cols, rows))
        for name, across, up in placements:
            if name == "player":
                if self.world.player is None:
                    self.player(across=across, up=up)
                else:
                    self.world.player.move_to(across, up)
                continue
            move = level_art.LEVEL_MOVES.get(name, "still")
            self.place(name, across, up, move=move)
        return self

    def levels(self, *texts):
        """Several level pictures in a row. Win one, the next one loads."""
        self._level_texts = list(texts)
        self.world.level_count = len(texts)
        if texts:
            self._load_level(0)
        return self

    def next_level(self):
        """Move on now, without waiting for the win rule."""
        if self._level_index + 1 < len(self._level_texts):
            self._load_level(self._level_index + 1)
            return True
        return False

    def _load_level(self, index):
        w = self.world
        self._level_index = index
        w.level_number = index + 1
        w.keys = 0
        w.won = False
        w.things = []
        w.player = None
        w.missed, w.collected = {}, {}
        self._start_time = None
        cfg = dict(self._player_cfg or {})
        self.level(self._level_texts[index])
        if w.player is None:            # the picture had no '@'
            self.player(shape=cfg.get("shape", "hero"),
                        control=cfg.get("control", "arrows"),
                        across=cfg.get("across"), up=cfg.get("up"))
        elif cfg:
            w.player.shape = cfg.get("shape") or w.player.shape
            w.control = cfg.get("control") or w.control
            w.gravity_on = w.control == "arrows+jump"
        w.say(f"Level {w.level_number}", 1.6)
        self._reset_extras()

    # ---- BLOCK 5: what happens when two things touch ---------------------
    def when_touch(self, thing, name):
        def deco(fn):
            self._touch_rules.append((thing, name, fn))
            return fn
        return deco

    def when_missed(self, name):
        def deco(fn):
            self._miss_rules[name] = fn
            return fn
        return deco

    # ---- the timer loop (a loop the kid writes as a decorator) -----------
    def every(self, seconds):
        def deco(fn):
            self._spawners.append([seconds, fn, 0.0])
            return fn
        return deco

    # ---- BLOCK 6: talking, winning, losing -------------------------------
    def say(self, text, seconds=2):
        """Put a message on the screen for a moment."""
        self.world.say(text, seconds)
        return self

    def win_when(self, condition):
        self._win_check = condition

    def win(self):
        self.world.won = True

    def over(self):
        self.world.over = True

    def score_reaches(self, target):
        def check(world, now):
            return world.score >= target
        return check

    def survived(self, seconds):
        def check(world, now):
            if self._start_time is None:
                self._start_time = now
            return (now - self._start_time) >= seconds
        return check

    def collected_all(self, name="coin"):
        def check(world, now):
            return len(world.alive_things(name)) == 0
        return check

    def reached(self, name="flag"):
        def check(world, now):
            p = world.player
            return bool(p) and any(p.touches(t) for t in world.alive_things(name))
        return check

    def jump_power(self, blocks):
        self.world.jump_blocks = blocks
        return self

    # ---- extra lives, appearing as you play ------------------------------
    def hearts(self, count=3, every=8, move="still", up=None):
        """Let extra lives appear while you play.

            game.hearts(3)              three hearts, one every 8 seconds
            game.hearts(5, every=4)     five hearts, one every 4 seconds
            game.hearts(0)              no extra lives at all

        Each heart turns up in a random EMPTY square, so it never hides
        inside a wall. `move="falls"` makes them drop in from the top
        instead (that's what a catching game wants).
        """
        if count < 0:
            raise errors.GameError(
                "The number of hearts can't be less than 0.\n"
                "Try: game.hearts(3)")
        self._heart_plan = (count, every, move, up)
        self._heart_budget = count
        if count == 0:
            return self

        def sprinkle():
            if self._heart_budget <= 0:
                return
            if move in ("falls", "falls_fast"):
                self._heart_budget -= 1
                self.drop("heart", move=move, speed=2)
                return
            spot = self.free_square(up=up)
            if spot is None:
                return                      # board is full; try again later
            self._heart_budget -= 1
            self.place("heart", spot[0], spot[1])

        self._spawners.append([every, sprinkle, 0.0])
        return self

    # ---- finding an empty square (useful on its own) ----------------------
    def is_free(self, across, up):
        """True if that grid square has nothing in it — no wall, no coin,
        not the player. Handy for placing things fairly."""
        w = self.world
        c = w.cell
        probe = Thing("probe", w.px(across) + c * 0.3, w.py(up) + c * 0.3,
                      w=c * 0.4, h=c * 0.4)
        return not any(probe.touches(t) for t in w.alive_things())

    def free_square(self, up=None, tries=80):
        """A random empty square, as (across, up). None if there isn't one."""
        n = self.cells
        for _ in range(tries):
            a = random.randint(0, n - 1)
            u = up if up is not None else random.randint(0, n - 1)
            if self.is_free(a, u):
                return (a, u)
        return None

    def _reset_extras(self):
        """Put the heart budget back. Called on restart and on a new level."""
        if self._heart_plan:
            self._heart_budget = self._heart_plan[0]

    # ---- internals -------------------------------------------------------
    def _check_grid(self, across, up):
        n = self.cells
        if not (0 <= across < n) or not (-1 <= up <= n):
            raise errors.off_grid(across, up, n)

    def _make(self, look, across, up, name=None, move="still", shape=None,
              speed=3, cells_w=1, cells_h=1):
        """Build one Thing from grid coordinates — the only pixel maths in the
        package that a kid never has to see."""
        w = self.world
        c = w.cell
        look = shape or look
        fw, fh = _SIZES.get(look, _DEFAULT_SIZE)
        pw, ph = c * fw, c * fh
        if look in ("wall", "block"):
            pw, ph = c, c
        if cells_w > 1:
            pw = c * cells_w if look in ("wall", "block", "platform", "spike") \
                else pw * cells_w
        if cells_h > 1:
            ph = c * cells_h if look in ("wall", "block") else ph * cells_h
        x = w.px(across) + max(0.0, (c - pw) / 2)
        y = w.py(up) + (c - ph)          # sit on the floor of its square
        t = Thing(name or look, x, y, move=move, shape=look,
                  w=pw, h=ph, speed=speed)
        return w.add(t)

    def _resize(self, cells):
        """Grow the grid to fit a bigger level picture, keeping the window."""
        w = self.world
        w.cells = cells
        w.cell = w.height / cells
        for t in w.things:
            t._cell = w.cell

    # ---- run it ----------------------------------------------------------
    def start(self):
        errors.install_soft_excepthook()
        if self.world.player is None:
            raise errors.no_player("Starting the game")
        from .renderer_pygame import run
        run(self)
