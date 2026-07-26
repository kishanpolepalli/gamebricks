"""The domain model: what a game IS, with zero rendering code.

Nothing here imports pygame. This is pure game state and rules, so the exact
same model can be driven by a desktop renderer today or a browser renderer
later. The renderer reads these objects; it never defines them.

ONE coordinate system, everywhere
---------------------------------
Kids place everything on a grid with `across` and `up`:

    across = 0  is the far LEFT column
    up     = 0  is the BOTTOM row

Like a graph in maths class. Pixels exist only inside this file and the
renderer; a kid never sees one.
"""

import math
import random

# The kid-facing vocabulary. Kept here so the API, the errors and the
# level-art legend all agree on one list.
SHAPES = (
    "hero", "basket", "ship", "star", "coin", "ghost", "wall",
    "platform", "flag", "block", "heart", "key", "door", "spike",
)
CONTROLS = ("arrows", "wasd", "mouse", "arrows+jump")
MOVES = ("still", "falls", "falls_fast", "drifts", "chases", "bounces")

SOLID_NAMES = ("wall", "platform", "block", "door")

# How long a thing ignores further touch rules after one fires (seconds).
# Without this, one bump with a ghost fires 60 times a second and eats every
# life you have before you can let go of the arrow key.
TOUCH_COOLDOWN = 0.6


class Thing:
    """One object in the game: the player, a star, a wall, the flag, a key.

    A kid never builds a Thing directly — `game.place(...)`, `game.coin(...)`
    and friends do it for them — but they DO hold on to what those return, so
    every method here has to read like plain English:

        star.burst()      hero.grow()      ghost.remove()
    """

    def __init__(self, name, x, y, move="still", shape=None,
                 w=28, h=28, speed=3):
        self.name = name
        self.shape = shape or name
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)
        self.move = move
        self.speed = speed
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.solid = move == "still" and name in SOLID_NAMES
        self.locked = name == "door"      # a door is solid until it opens
        self.needs = 1                   # keys a door wants before it opens
        self.message = None              # speech bubble text
        self._message_left = 0.0         # seconds of bubble remaining
        self._cool = 0.0                 # touch-rule cooldown remaining
        self._bursting = 0               # frames of sparkle burst remaining
        self._burst_parts = []

    def __repr__(self):
        return f"<{self.name} across={self.across} up={self.up}>"

    # ---- geometry ---------------------------------------------------------
    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    @property
    def across(self):
        """Which grid column this thing is standing in (0 = far left)."""
        return int(self.cx // self._cell) if self._cell else 0

    @property
    def up(self):
        """Which grid row this thing is standing in (0 = bottom)."""
        if not self._cell or not self._world_h:
            return 0
        return int((self._world_h - self.cy) // self._cell)

    # the grid the thing lives on; set by World.add so `across`/`up` work
    _cell = 0.0
    _world_h = 0.0

    def touches(self, other):
        """Axis-aligned box overlap — the one collision test the game needs."""
        return (self.x < other.x + other.w and self.x + self.w > other.x and
                self.y < other.y + other.h and self.y + self.h > other.y)

    def blocks_movement(self):
        """Solid things stop the player. An unlocked door does not."""
        if not self.alive:
            return False
        if self.name == "door":
            return self.locked
        return self.solid

    # ---- movement (per frame) --------------------------------------------
    def update(self, world, dt=1 / 60):
        if not self.alive:
            return

        if self._cool > 0:
            self._cool = max(0.0, self._cool - dt)
        if self._message_left > 0:
            self._message_left -= dt
            if self._message_left <= 0:
                self.message = None

        m = self.move
        if m == "falls":
            self.y += self.speed
        elif m == "falls_fast":
            self.y += self.speed * 2.2
        elif m == "drifts":
            self.x += self.vx or self.speed
            if self.x < 0 or self.x + self.w > world.width:
                self.vx = -(self.vx or self.speed)
        elif m == "chases":
            p = world.player
            if p:
                dx, dy = p.cx - self.cx, p.cy - self.cy
                d = math.hypot(dx, dy) or 1
                self.x += dx / d * (self.speed * 0.6)
                self.y += dy / d * (self.speed * 0.6)
        elif m == "bounces":
            self.x += self.vx or self.speed
            self.y += self.vy or self.speed
            if self.x < 0 or self.x + self.w > world.width:
                self.vx = -(self.vx or self.speed)
            if self.y < 0 or self.y + self.h > world.height:
                self.vy = -(self.vy or self.speed)
        # "still" does nothing, on purpose.

        # burst animation countdown
        if self._bursting > 0:
            self._bursting -= 1
            for pt in self._burst_parts:
                pt[0] += pt[2]
                pt[1] += pt[3]
            if self._bursting == 0:
                self.alive = False

    # ---- kid-callable effects --------------------------------------------
    def burst(self):
        """Explode into sparkles, then disappear. The 'juice'."""
        if self._bursting:
            return
        self._bursting = 14
        self._burst_parts = [
            [self.cx, self.cy, random.uniform(-3, 3), random.uniform(-3, 3)]
            for _ in range(12)
        ]

    def remove(self):
        self.alive = False

    def say(self, text, seconds=2):
        """Pop a little speech bubble above this thing."""
        self.message = str(text)
        self._message_left = seconds
        return self

    def grow(self):
        self.w = min(self.w * 1.15, 120)
        self.h = min(self.h * 1.15, 120)
        return self

    def shrink(self):
        self.w = max(self.w * 0.9, 6)
        self.h = max(self.h * 0.9, 6)
        return self

    def open(self):
        """Unlock a door."""
        self.locked = False
        return self

    def move_to(self, across, up):
        """Jump straight to a grid square. Handy for `hero.move_to(0, 0)`."""
        c = self._cell or 1
        self.x = across * c + (c - self.w) / 2
        self.y = self._world_h - (up + 1) * c + (c - self.h) / 2
        return self


class World:
    """Holds everything: the player, all things, the score, the rules.

    Still no pygame here — just state. The renderer takes a World and draws it.
    """

    def __init__(self, width=640, height=640, cells=8):
        self.width = width
        self.height = height
        self.cells = cells
        self.cell = height / cells
        self.player = None
        self.things = []
        self.score = 0
        self.lives = 3
        self.keys = 0
        self.control = "arrows"
        self.jump_blocks = 3
        self.gravity_on = False
        self.show_grid = False
        self.sound_on = True
        self.title = "GameBricks Game"
        self.level_number = 1
        self.level_count = 1
        self.won = False
        self.over = False
        self.message = None
        self.message_left = 0.0
        self.missed = {}              # name -> how many fell off the screen
        self.collected = {}           # name -> how many the player picked up

    # ---- grid <-> pixels (the only place this maths lives) ----------------
    def px(self, across):
        return across * self.cell

    def py(self, up):
        """Pixel y of the TOP of grid row `up` (0 = bottom row)."""
        return self.height - (up + 1) * self.cell

    def add(self, thing):
        thing._cell = self.cell
        thing._world_h = self.height
        self.things.append(thing)
        return thing

    def alive_things(self, name=None):
        return [t for t in self.things
                if t.alive and (name is None or t.name == name)]

    def solid_things(self):
        return [t for t in self.things if t.blocks_movement()]

    def say(self, text, seconds=2):
        self.message = str(text)
        self.message_left = seconds

    def prune(self):
        """Forget things that are dead and finished animating.

        Without this, a catch game that has been running for ten minutes is
        dragging thousands of invisible dead stars around every frame.
        """
        self.things = [t for t in self.things if t.alive or t._bursting > 0]
