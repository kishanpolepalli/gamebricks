"""Little sounds, made out of maths — no sound files to download.

Every sound is a short beep built as raw samples, so the package stays a
single pip install. If the machine has no audio (a school laptop with sound
disabled, a test runner, a Raspberry Pi with no card) everything here quietly
does nothing instead of crashing a kid's game.
"""

import array
import math

_RATE = 22050
_cache = {}
_mixer = None          # the pygame.mixer module, once it works
_broken = False

# name -> (start hz, end hz, seconds, wave)
RECIPES = {
    "score": (660, 990, 0.10, "square"),
    "coin": (880, 1320, 0.09, "square"),
    "key": (990, 1480, 0.12, "square"),
    "door": (300, 520, 0.18, "square"),
    "bump": (240, 120, 0.14, "saw"),
    "jump": (420, 720, 0.10, "square"),
    "win": (520, 1040, 0.45, "square"),
    "lose": (400, 130, 0.50, "saw"),
    "burst": (1200, 300, 0.12, "saw"),
    "beep": (700, 700, 0.07, "square"),
}


def _samples(start, end, seconds, wave):
    n = int(_RATE * seconds)
    buf = array.array("h")
    for i in range(n):
        t = i / n
        hz = start + (end - start) * t
        phase = (i * hz / _RATE) % 1.0
        if wave == "square":
            v = 1.0 if phase < 0.5 else -1.0
        else:  # saw
            v = 2.0 * phase - 1.0
        fade = min(1.0, (1.0 - t) * 4)          # soft tail, no clicks
        attack = min(1.0, t * 40)
        s = int(v * 7000 * fade * attack)
        buf.append(s)
        buf.append(s)                            # stereo
    return buf


def init():
    """Try once to open the mixer. Failure is fine and permanent."""
    global _mixer, _broken
    if _mixer is not None or _broken:
        return _mixer
    try:
        import pygame
        pygame.mixer.pre_init(_RATE, -16, 2, 256)
        pygame.mixer.init()
        _mixer = pygame.mixer
    except Exception:
        _broken = True
    return _mixer


def play(name, on=True):
    """Play one of the named beeps. Unknown names are ignored on purpose —
    a typo in a sound name should never stop a game."""
    if not on or name not in RECIPES:
        return
    mixer = init()
    if mixer is None:
        return
    try:
        snd = _cache.get(name)
        if snd is None:
            snd = mixer.Sound(buffer=_samples(*RECIPES[name]).tobytes())
            snd.set_volume(0.35)
            _cache[name] = snd
        snd.play()
    except Exception:
        pass
