"""Level text-art: draw a whole level with your keyboard.

A kid types a picture and gets a level. One character = one grid square, and
the picture on screen matches the picture in their file, right way up:

    game.level('''
    ########
    #..c..d#
    #.####.#
    #.k....#
    #.####.#
    #@....c#
    ########
    ''')

The default legend (they can add their own with `game.legend(x="ghost")`):

    #  wall        .  empty space   @  the player
    c  coin        k  key           d  door
    *  star        g  ghost         =  platform
    F  flag        H  heart         ^  spike
"""

from . import errors

DEFAULT_LEGEND = {
    "#": "wall",
    "=": "platform",
    "c": "coin",
    "k": "key",
    "d": "door",
    "*": "star",
    "g": "ghost",
    "F": "flag",
    "H": "heart",
    "^": "spike",
    "@": "player",
}

EMPTY = (".", " ", "-", "_")

# Things that should drift/chase rather than sit still when drawn in a level.
LEVEL_MOVES = {"ghost": "chases"}


def parse(text, legend=None):
    """Turn text art into a list of (character, across, up) placements.

    Rows are read top-to-bottom in the text but reported as `up` counted from
    the bottom, so what a kid draws is what a kid sees.
    """
    marks = dict(DEFAULT_LEGEND)
    if legend:
        marks.update(legend)

    rows = [r for r in str(text).splitlines() if r.strip()]
    if not rows:
        raise errors.empty_level()

    # strip the common leading indent so a triple-quoted string inside a
    # function still lines up
    indent = min(len(r) - len(r.lstrip()) for r in rows)
    rows = [r[indent:] for r in rows]

    height = len(rows)
    width = max(len(r) for r in rows)
    placements = []
    for row_index, row in enumerate(rows):
        up = height - 1 - row_index
        for across, ch in enumerate(row):
            if ch in EMPTY:
                continue
            if ch not in marks:
                raise errors.unknown_mark(ch, marks)
            placements.append((marks[ch], across, up))
    return placements, width, height
