"""The pygame renderer — the ONLY file that knows about pygame.

Everything else in the package is engine-agnostic. Swapping this file for a
browser renderer later would not change one line of a kid's game code.

Responsibilities:
  * open a window and run the game loop (the kid never writes this)
  * draw the World: every Thing, the grid, the HUD, speech bubbles
  * handle keyboard/mouse input for the chosen control mode
  * run spawn timers, collision rules, win/lose checks, level changes
  * the keys a grown-up always wishes were there: R restart, P pause
"""

import math

from . import sounds
from .model import TOUCH_COOLDOWN

# Colours keyed by shape, so every shape looks decent with zero kid effort.
_COLORS = {
    "hero": (142, 208, 160),
    "basket": (142, 208, 160),
    "ship": (142, 208, 160),
    "star": (255, 216, 74),
    "coin": (255, 216, 74),
    "ghost": (180, 140, 255),
    "wall": (42, 51, 88),
    "platform": (42, 51, 88),
    "flag": (255, 107, 107),
    "block": (100, 116, 139),
    "heart": (255, 120, 160),
    "key": (255, 196, 92),
    "door": (150, 110, 70),
    "spike": (226, 90, 90),
}
_BG = (13, 16, 32)
_GRID = (30, 38, 66)
_INK = (255, 255, 255)
_DIM = (154, 164, 192)

# Names the engine knows what to do with, so a game works before a kid has
# written a single rule. Any name they DO write a rule for wins instead.
_AUTO = ("coin", "star", "key", "door", "flag", "heart", "spike", "ghost")


# ---------------------------------------------------------------- drawing --
def _draw_thing(pg, screen, t, font):
    col = _COLORS.get(t.shape, (200, 200, 200))
    x, y, w, h = int(t.x), int(t.y), int(t.w), int(t.h)

    if t._bursting > 0:
        for px, py, *_ in t._burst_parts:
            r = max(1, int(3 * t._bursting / 14))
            pg.draw.circle(screen, col, (int(px), int(py)), r)
        return

    if t.shape in ("star", "coin"):
        _star(pg, screen, t.cx, t.cy, max(w, h) / 2, col)
    elif t.shape == "key":
        pg.draw.circle(screen, col, (x + h // 2, int(t.cy)), max(3, h // 3), 2)
        pg.draw.rect(screen, col, (x + h - 2, int(t.cy) - 2, w - h + 2, 3))
        pg.draw.rect(screen, col, (x + w - 6, int(t.cy), 3, 5))
    elif t.shape == "door":
        pg.draw.rect(screen, col, (x, y, w, h), border_radius=4)
        knob = (255, 230, 150) if not t.locked else (90, 70, 50)
        pg.draw.circle(screen, knob, (x + w - 7, int(t.cy)), 3)
        if t.locked:
            pg.draw.rect(screen, (70, 52, 38), (x + 4, y + 4, w - 8, h - 8), 2)
    elif t.shape == "spike":
        step = max(8, w // max(1, w // 12))
        for sx in range(x, x + w - 2, step):
            pg.draw.polygon(screen, col, [(sx, y + h),
                                          (sx + step / 2, y),
                                          (sx + step, y + h)])
    elif t.shape == "heart":
        r = max(3, h // 3)
        pg.draw.circle(screen, col, (x + r, y + r), r)
        pg.draw.circle(screen, col, (x + w - r, y + r), r)
        pg.draw.polygon(screen, col, [(x, y + r), (x + w, y + r),
                                      (int(t.cx), y + h)])
    elif t.shape == "flag":
        pg.draw.rect(screen, (74, 86, 136), (x, y, 3, h))
        pg.draw.polygon(screen, col, [(x + 3, y), (x + w, y + h * 0.3),
                                      (x + 3, y + h * 0.6)])
    elif t.shape == "ghost":
        pg.draw.circle(screen, col, (int(t.cx), int(t.cy)), w // 2)
        pg.draw.rect(screen, col, (x, int(t.cy), w, h // 2))
        pg.draw.circle(screen, _BG, (int(t.cx - 4), int(t.cy - 2)), 2)
        pg.draw.circle(screen, _BG, (int(t.cx + 4), int(t.cy - 2)), 2)
    elif t.shape == "basket":
        pg.draw.rect(screen, col, (x, y, w, h), border_radius=6)
        pg.draw.rect(screen, _BG, (x + 4, y, w - 8, max(3, h // 4)))
    elif t.shape in ("hero", "ship"):
        pg.draw.circle(screen, col, (int(t.cx), int(t.cy)), max(w, h) // 2)
        pg.draw.circle(screen, _BG, (int(t.cx - 4), int(t.cy - 3)), 2)
        pg.draw.circle(screen, _BG, (int(t.cx + 4), int(t.cy - 3)), 2)
    else:
        pg.draw.rect(screen, col, (x, y, w, h))

    if t.message:
        _bubble(pg, screen, font, t.message, int(t.cx), y - 6)


def _star(pg, screen, cx, cy, r, col):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    pg.draw.polygon(screen, col, pts)


def _bubble(pg, screen, font, text, cx, bottom):
    label = font.render(str(text), True, (20, 24, 44))
    pad = 6
    w, h = label.get_width() + pad * 2, label.get_height() + pad
    x, y = cx - w // 2, bottom - h
    pg.draw.rect(screen, (240, 243, 255), (x, y, w, h), border_radius=6)
    pg.draw.polygon(screen, (240, 243, 255),
                    [(cx - 4, y + h), (cx + 4, y + h), (cx, y + h + 5)])
    screen.blit(label, (x + pad, y + pad // 2))


def _draw_grid(pg, screen, w, font):
    c = w.cell
    for i in range(w.cells + 1):
        p = int(i * c)
        pg.draw.line(screen, _GRID, (p, 0), (p, w.height))
        pg.draw.line(screen, _GRID, (0, p), (w.width, p))
    for i in range(w.cells):
        across = font.render(str(i), True, _GRID)
        screen.blit(across, (int(i * c) + 4, w.height - 16))
        up = font.render(str(w.cells - 1 - i), True, _GRID)
        screen.blit(up, (4, int(i * c) + 3))


# ------------------------------------------------------------------- loop --
def run(game):
    import pygame as pg

    sounds.init()
    pg.init()
    w = game.world
    screen = pg.display.set_mode((int(w.width), int(w.height)))
    pg.display.set_caption(w.title)
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 26)
    small = pg.font.SysFont(None, 18)
    big = pg.font.SysFont(None, 52)

    snapshot = _snapshot(game)
    running, paused = True, False
    now = 0.0
    ended = None                     # "win" | "over", so sounds fire once

    while running:
        dt = clock.tick(60) / 1000.0
        keys = pg.key.get_pressed()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    running = False
                elif e.key == pg.K_r:
                    _restore(game, snapshot)
                    now, ended, paused = 0.0, None, False
                elif e.key == pg.K_p:
                    paused = not paused
                elif e.key == pg.K_g:
                    w.show_grid = not w.show_grid
                elif e.key == pg.K_m:
                    w.sound_on = not w.sound_on
                elif e.key in (pg.K_SPACE, pg.K_UP) and w.gravity_on:
                    _jump(game, pg)

        live = not (w.won or w.over) and not paused
        if live:
            now += dt
            _step(game, pg, keys, dt, now)

        # ---- draw ----
        screen.fill(_BG)
        if w.show_grid:
            _draw_grid(pg, screen, w, small)
        for t in w.things:
            if t.alive or t._bursting > 0:
                _draw_thing(pg, screen, t, small)
        _hud(pg, screen, font, small, w, now)

        if w.message and w.message_left > 0:
            w.message_left -= dt
            _center_text(pg, screen, font, w.message, w.height * 0.22,
                         (255, 255, 255))
            if w.message_left <= 0:
                w.message = None

        if w.won and ended != "win":
            ended = "win"
            sounds.play("win", w.sound_on)
        if w.over and ended != "over":
            ended = "over"
            sounds.play("lose", w.sound_on)

        if w.won:
            _banner(pg, screen, big, small, "You win!", (142, 208, 160))
        elif w.over:
            _banner(pg, screen, big, small, "Game over", (255, 107, 107))
        elif paused:
            _banner(pg, screen, big, small, "Paused", (255, 216, 74))

        pg.display.flip()

    pg.quit()


def _hud(pg, screen, font, small, w, now):
    parts = [f"Score {w.score}", f"Lives {w.lives}"]
    if any(t.name in ("key", "door") for t in w.things):
        parts.append(f"Keys {w.keys}")
    if w.level_count > 1:
        parts.append(f"Level {w.level_number}/{w.level_count}")
    label = font.render("   ".join(parts), True, _INK)
    screen.blit(label, (12, 10))
    hint = small.render("R restart   P pause   G grid   M mute   Esc quit",
                        True, _DIM)
    screen.blit(hint, (12, int(w.height) - 20))


def _center_text(pg, screen, font, text, y, col):
    label = font.render(str(text), True, col)
    screen.blit(label, (screen.get_width() // 2 - label.get_width() // 2, int(y)))


# ------------------------------------------------------------------ rules --
def _step(game, pg, keys, dt, now):
    w = game.world

    if w.gravity_on:
        _platformer(game, pg, keys)
    else:
        _walk(game, pg, keys)

    for spawner in game._spawners:
        interval, fn, _acc = spawner
        spawner[2] += dt
        if spawner[2] >= interval:
            spawner[2] = 0.0
            fn()

    for t in list(w.things):
        t.update(w, dt)
        if t.alive and t.move in ("falls", "falls_fast") and t.y > w.height:
            t.alive = False
            w.missed[t.name] = w.missed.get(t.name, 0) + 1
            fn = game._miss_rules.get(t.name)
            if fn:
                fn()

    _touches(game, dt)
    w.prune()

    if game._win_check and game._win_check(w, now):
        if not game.next_level():
            w.won = True
    if w.lives <= 0:
        w.over = True


def _touches(game, dt):
    w = game.world
    p = w.player
    if not p:
        return
    handled = set()

    for owner, name, fn in game._touch_rules:
        thing = p if (owner is None or owner.name == "player") else owner
        thing = w.player if thing is p else thing
        handled.add(name)
        for t in w.alive_things(name):
            if t is thing or t._bursting or t._cool > 0:
                continue
            if thing.touches(t):
                t._cool = TOUCH_COOLDOWN
                _run_touch(fn, t)

    # built-in behaviour for anything the kid hasn't written a rule for,
    # so placing a coin does something the moment they place it
    for t in w.alive_things():
        if t.name in handled or t.name not in _AUTO or t is p:
            continue
        if t._bursting or t._cool > 0 or not p.touches(t):
            continue
        t._cool = TOUCH_COOLDOWN
        _auto_touch(game, t)


def _auto_touch(game, t):
    w = game.world
    on = w.sound_on
    if t.name in ("coin", "star"):
        w.score += 1
        w.collected[t.name] = w.collected.get(t.name, 0) + 1
        sounds.play("coin", on)
        t.burst()
    elif t.name == "key":
        w.keys += 1
        sounds.play("key", on)
        t.burst()
        for door in w.alive_things("door"):
            if door.locked and w.keys >= getattr(door, "needs", 1):
                door.open()
                door.say("open!", 1.4)
                sounds.play("door", on)
    elif t.name == "door":
        if not t.locked:
            if not game.next_level():
                w.won = True
        else:
            need = getattr(t, "needs", 1)
            t.say(f"need {need - w.keys} key(s)", 1.4)
            sounds.play("bump", on)
    elif t.name == "flag":
        if not game.next_level():
            w.won = True
    elif t.name == "heart":
        w.lives += 1
        sounds.play("score", on)
        t.burst()
    elif t.name in ("spike", "ghost"):
        w.lives -= 1
        sounds.play("bump", on)


def _run_touch(fn, thing):
    import inspect
    n = len(inspect.signature(fn).parameters)
    fn(thing) if n >= 1 else fn()


# ------------------------------------------------------------- movement ----
def _walk(game, pg, keys):
    """Top-down / side-to-side movement, blocked by solid things."""
    w = game.world
    p = w.player
    if not p:
        return
    speed = 5
    solids = [t for t in w.solid_things() if t is not p]

    def blocked(nx, ny):
        ox, oy = p.x, p.y
        p.x, p.y = nx, ny
        hit = any(p.touches(s) for s in solids)
        p.x, p.y = ox, oy
        return hit

    if w.control == "mouse":
        mx, _my = pg.mouse.get_pos()
        nx = mx - p.w / 2
        if not blocked(nx, p.y):
            p.x = nx
    else:
        wasd = w.control == "wasd"
        left = keys[pg.K_LEFT] or (wasd and keys[pg.K_a])
        right = keys[pg.K_RIGHT] or (wasd and keys[pg.K_d])
        up = keys[pg.K_UP] or (wasd and keys[pg.K_w])
        down = keys[pg.K_DOWN] or (wasd and keys[pg.K_s])
        # one axis at a time, so you slide along a wall instead of sticking
        if left and not blocked(p.x - speed, p.y):
            p.x -= speed
        if right and not blocked(p.x + speed, p.y):
            p.x += speed
        if up and not blocked(p.x, p.y - speed):
            p.y -= speed
        if down and not blocked(p.x, p.y + speed):
            p.y += speed

    p.x = max(0, min(w.width - p.w, p.x))
    p.y = max(0, min(w.height - p.h, p.y))


def _pf_state(game):
    st = getattr(game, "_pf", None)
    if st is None:
        st = {"vy": 0.0, "on_ground": False}
        game._pf = st
    return st


def _jump(game, pg):
    w = game.world
    st = _pf_state(game)
    if st["on_ground"] and w.player:
        st["vy"] = -math.sqrt(2 * 0.5 * (w.jump_blocks * w.cell + 8))
        st["on_ground"] = False
        sounds.play("jump", w.sound_on)


def _platformer(game, pg, keys):
    """Gravity + jump + landing on platforms."""
    w = game.world
    p = w.player
    if not p:
        return
    st = _pf_state(game)
    speed = 4
    solids = [t for t in w.solid_things() if t is not p]

    for dx, pressed in ((-speed, keys[pg.K_LEFT] or keys[pg.K_a]),
                        (speed, keys[pg.K_RIGHT] or keys[pg.K_d])):
        if not pressed:
            continue
        p.x += dx
        for s in solids:
            if p.touches(s) and s.name != "platform":
                p.x -= dx
                break
    p.x = max(0, min(w.width - p.w, p.x))

    st["vy"] = min(st["vy"] + 0.5, 18)
    p.y += st["vy"]
    st["on_ground"] = False
    for s in solids:
        if (p.x + p.w > s.x and p.x < s.x + s.w and st["vy"] >= 0
                and p.y + p.h > s.y and p.y + p.h < s.y + s.h + 18
                and p.y < s.y):
            p.y = s.y - p.h
            st["vy"] = 0
            st["on_ground"] = True
    if p.y > w.height + 60:                    # fell off -> back to the start
        cfg = game._player_cfg or {}
        p.move_to(cfg.get("across") or 0, cfg.get("up") or 1)
        st["vy"] = 0
        w.lives -= 1
        sounds.play("bump", w.sound_on)


# --------------------------------------------------------------- restart ---
def _snapshot(game):
    w = game.world
    return {
        "score": 0, "lives": w.lives, "keys": 0,
        "level": game._level_index,
        "things": [(t.name, t.shape, t.x, t.y, t.w, t.h, t.move, t.speed,
                    t.locked, t is w.player, getattr(t, "needs", 1))
                   for t in w.things],
    }


def _restore(game, snap):
    from .model import Thing
    w = game.world
    if game._level_texts:
        game._load_level(snap["level"])
    else:
        w.things = []
        w.player = None
        for (name, shape, x, y, tw, th, move, speed, locked,
             is_player, needs) in snap["things"]:
            t = Thing(name, x, y, move=move, shape=shape, w=tw, h=th,
                      speed=speed)
            t.locked = locked
            t.needs = needs
            w.add(t)
            if is_player:
                w.player = t
    w.score, w.lives, w.keys = snap["score"], snap["lives"], snap["keys"]
    w.won = w.over = False
    w.missed, w.collected = {}, {}
    w.message, w.message_left = None, 0.0
    game._start_time = None
    game._reset_extras()
    game._pf = {"vy": 0.0, "on_ground": False}
    for s in game._spawners:
        s[2] = 0.0


def _banner(pg, screen, big, small, text, color):
    w, h = screen.get_size()
    overlay = pg.Surface((w, h))
    overlay.set_alpha(200)
    overlay.fill(_BG)
    screen.blit(overlay, (0, 0))
    label = big.render(text, True, color)
    screen.blit(label, (w // 2 - label.get_width() // 2, h // 2 - 34))
    hint = small.render("press R to play again   ·   Esc to close", True, _DIM)
    screen.blit(hint, (w // 2 - hint.get_width() // 2, h // 2 + 24))
