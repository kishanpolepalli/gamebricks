# Evaluation of the original package, and what changed

## What was already good

- Clean separation: `model.py` had zero pygame, so the game was testable and a
  browser renderer stayed possible. That decision is kept and leaned on harder.
- `errors.py` was the best idea in the package — friendly, fix-included
  messages. Extended rather than replaced.
- The decorator API (`@game.every`, `@game.when_touch`) reads like English and
  teaches loops and conditions honestly.

## What blocked the goal ("kids customise by changing positions")

| Problem | Why it hurt | Now |
|---|---|---|
| **Two coordinate systems.** `platform/flag/coin` used `height` counted from the bottom; the maze builder used rows counted from the top. | A kid moving things had to hold two mental models. | **One system everywhere:** `across` (0 = left), `up` (0 = bottom). Used by the player, walls, coins, doors, platforms, spikes, level art — everything. |
| **Most things couldn't be positioned at all.** `spawn()` randomised x and y. | The headline ask was impossible for stars, ghosts, hearts. | `game.place(name, across, up, ...)` is the one placement command; `coin/key/door/flag/heart/ghost/wall/platform/spike/row/border/ground` are shortcuts for it. |
| **The maze was hardcoded** inside `game.py` as a private 10×10 string. | The most customisable artifact in the package was the one a kid couldn't touch. | `game.level("""…""")` — text art, one character per square, drawn right way up. `game.legend(x="ghost")` extends it. |
| **Examples reached into `game._cell`** and did their own pixel maths. | Signalled the public API wasn't enough. | No example touches a private attribute or a pixel. |
| **No way to see the grid.** | "across=3" was abstract. | `game.show_grid()` (or **G** while playing) draws the grid with the numbers printed on both axes. |
| Grid was fixed at 10 | — | `Game(cells=8)`, default 8, any size. |

## Bugs fixed

- **Touching a ghost cost every life at once.** `burst()` left `alive = True`
  for 14 frames, so `when_touch` re-fired 60×/second. Added a 0.6s per-thing
  touch cooldown; bursting things are skipped.
- **`maze.py` created two players.** The first was orphaned but still drawn and
  still collided. A second `player()` call now replaces the first.
- **Dead things were never removed** from `world.things` — a ten-minute catch
  game dragged thousands of invisible corpses through every frame.
  `World.prune()` runs each frame.
- **`collected_all()` computed a target it never used**; `world._missed` was
  written by nothing. Both are now real (`world.missed`, `world.collected`).
- **Falling off in the platformer was free** — you respawned with no cost and
  no feedback. Now costs a life and plays a bump.
- **No way to replay.** You had to quit the window and re-run Python. **R**
  restarts, **P** pauses, **M** mutes.
- `spawn(at="top")` and `spawn_many(layout=...)` were magic strings that
  contradicted the grid API; replaced by `drop()` and `level()`.

## What was added to make it interesting

- **Ready-made games in one line** — `python -m gamebricks maze`,
  `gamebricks.play("chase")`, or `gamebricks.load("platformer")` to get a working
  game and change it before starting. This is the on-ramp: a kid plays
  something first, then edits it, then writes their own.
- **Default behaviour for every artifact**, so placing a thing *does* something
  before any rule is written: a coin scores, a heart gives a life, a spike
  costs one, a flag wins, a key opens a door. A kid's own `when_touch` rule for
  that name takes over when they write one.
- **Keys and doors.** A door stays shut, says how many keys it still wants, and
  opens when you have them.
- **Multiple levels.** `game.levels(a, b, c)` — win one, the next picture loads.
- **Speech and messages.** `game.say("nice!")` and `hero.say("ouch")` — the
  cheapest way to make a game feel alive, and it teaches strings.
- **Sound**, generated as maths (no audio files, no extra download, silent and
  safe on machines with no audio card).
- **New shapes:** key, door, spike, plus heart wired up.
- **Seven examples in learning order**, each ending in a `# TRY THIS` list of
  three edits with a visible consequence.
- **Hearts that appear during play**, with the count under the kid's control:
  `game.hearts(3)`, `game.hearts(6, every=4)`, `game.hearts(0)`. Each one lands
  in a random *empty* square (`game.free_square()` / `game.is_free()` are public
  for the same reason), refills on a new level and on restart, and can fall in
  from the top instead (`move="falls"`) for catching games.
- **One shape for every game.** All five ready-made games and all seven
  examples are written in the same order — board, player, level, hearts, rules,
  one win rule — and keep the same promises: 3 lives, always losable, exactly
  one win rule, same hotkeys. Learning the second game is nearly free.
- **Headless test suite** covering the grid maths, level parsing, the friendly
  errors, the heart budget, the cross-game contract, and every bug above — it
  runs without pygame or a display.

## Deliberately not done

- No drag-to-place editor. You chose "edit numbers and re-run", which keeps the
  text file the single source of truth — a drag tool teaches dragging, not code.
- No new movement types beyond the original six. The dial count is already at
  the edge of what fits on one cheat sheet.
