"""Gentle errors: every mistake becomes a tiny, friendly lesson.

Rule: point at the code, never blame the child, always show the fix,
never end on the problem.
"""

import difflib


class GameError(Exception):
    """An error a kid can actually read."""

    def __str__(self):
        return self.args[0] if self.args else "Something went wrong."


def _did_you_mean(word, options):
    match = difflib.get_close_matches(str(word), list(options), n=1, cutoff=0.4)
    return match[0] if match else None


def unknown(kind, got, options):
    """Build a friendly 'I don't know X' error with a 'did you mean'."""
    label = {"shape": "shape", "control": "control", "move": "movement",
             "game": "game"}.get(kind, kind)
    msg = (f"Oops — I don't know the {label} '{got}'.\n"
           f"Try one of these: {', '.join(options)}.")
    guess = _did_you_mean(got, options)
    if guess:
        msg += f"\n(did you mean '{guess}'?)"
    return GameError(msg)


def unknown_mark(ch, legend):
    known = " ".join(sorted(legend))
    # the fix we print has to be code they can actually paste, so a letter
    # becomes a keyword argument and a symbol becomes the dictionary form
    if str(ch).isidentifier():
        fix = f'game.legend({ch}="ghost")'
    else:
        fix = f'game.legend(**{{"{ch}": "ghost"}})'
    return GameError(
        f"In your level picture I found the character '{ch}',\n"
        f"but I don't know what to build for it.\n"
        f"Characters I know: {known}  (and . for empty space)\n"
        f"You can teach me a new one:  {fix}"
    )


def empty_level(*_):
    return GameError(
        "Your level picture is empty, so there's nothing to build.\n"
        "Try drawing a small room first:\n"
        '    game.level("""\n'
        "    ####\n"
        "    #@c#\n"
        "    ####\n"
        '    """)'
    )


def off_grid(across, up, cells):
    return GameError(
        f"You asked me to put something at across={across}, up={up},\n"
        f"but this grid only goes from 0 to {cells - 1} in both directions.\n"
        f"Pick smaller numbers — or make the grid bigger with "
        f"Game(cells={max(across, up) + 1})."
    )


def needs_number(what, example):
    return GameError(f"{what} needs to be a number.\nTry: {example}")


def no_player(what):
    return GameError(
        f"{what} needs a player first.\n"
        'Add this line above it:  hero = game.player(shape="hero")'
    )


def install_soft_excepthook():
    """Replace the scary traceback with a gentle top line for uncaught errors
    in a kid's program. Keeps the real error visible for a grown-up."""
    import sys

    default = sys.excepthook

    def soft(exc_type, exc, tb):
        if isinstance(exc, GameError):
            print(f"\n{exc}\n")
            return
        name = exc_type.__name__
        if name == "SyntaxError":
            print("\nAlmost! Python got a little confused.")
            print("Check for a missing ':' at the end of a for/if/def line,")
            print("or a bracket that isn't closed.\n")
            return
        if name == "IndentationError":
            print("\nA line inside your loop or 'if' needs to be pushed in.")
            print("Press Tab once so it sits under the line above it.\n")
            return
        if name == "NameError":
            missing = str(exc).split("'")[1] if "'" in str(exc) else "that"
            print(f"\nYou used '{missing}', but I never learned what it means.")
            print(f"Give it a value first, above this line. Like: {missing} = 3\n")
            return
        if name == "TypeError" and "positional" in str(exc):
            print("\nOne of your lines has the wrong number of things in the "
                  "brackets.")
            print("Check the example in the cheat sheet and compare it to "
                  "your line.\n")
            return
        print("\nSomething unexpected happened. Show a grown-up this:")
        default(exc_type, exc, tb)

    sys.excepthook = soft
