"""Tests that never open a window, so they run anywhere (no pygame needed).

Everything checked here is engine-agnostic: grid maths, level parsing,
friendly errors, and the rules that used to be bugs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

import gamebricks
from gamebricks import Game, GameError
from gamebricks.level import parse
from gamebricks.model import TOUCH_COOLDOWN


# ---- one coordinate system ------------------------------------------------
def test_across_and_up_round_trip():
    game = Game(cells=8, size=640)
    coin = game.coin(across=3, up=5)
    assert (coin.across, coin.up) == (3, 5)


def test_up_zero_is_the_bottom_row():
    game = Game(cells=8, size=640)
    low = game.coin(across=0, up=0)
    high = game.coin(across=0, up=7)
    assert low.y > high.y  # bigger pixel y = lower on screen


def test_off_grid_is_a_friendly_error():
    game = Game(cells=8)
    with pytest.raises(GameError) as e:
        game.coin(across=99, up=2)
    assert "only goes from 0 to 7" in str(e.value)


def test_unknown_shape_suggests_a_fix():
    game = Game()
    with pytest.raises(GameError) as e:
        game.player(shape="basktet")
    assert "basket" in str(e.value)


# ---- level text art -------------------------------------------------------
def test_level_art_is_the_right_way_up():
    placements, cols, rows = parse("""
        ###
        #c#
        #@#
        ###
    """)
    assert (cols, rows) == (3, 4)
    coin = [p for p in placements if p[0] == "coin"][0]
    player = [p for p in placements if p[0] == "player"][0]
    assert coin[2] > player[2]  # the coin is drawn above the player


def test_unknown_character_teaches_the_legend():
    with pytest.raises(GameError) as e:
        parse("#z#")
    assert "game.legend" in str(e.value)


def test_level_builds_things_and_places_the_player():
    game = Game(cells=4)
    game.level("""
        ####
        #@c#
        #..#
        ####
    """)
    assert game.world.player is not None
    assert len(game.world.alive_things("coin")) == 1
    assert len(game.world.alive_things("wall")) == 12


def test_custom_legend():
    game = Game(cells=3)
    game.legend(x="ghost")
    game.level("xxx")
    assert len(game.world.alive_things("ghost")) == 3


# ---- the bugs that used to bite ------------------------------------------
def test_second_player_call_replaces_the_first():
    game = Game()
    game.player(shape="hero")
    game.player(shape="hero")
    assert len([t for t in game.world.things if t.name == "player"]) == 1


def test_dead_things_are_pruned():
    game = Game()
    game.player()
    star = game.coin(across=1, up=1)
    star.remove()
    game.world.prune()
    assert star not in game.world.things


def test_touch_cooldown_exists_so_one_bump_is_one_hit():
    game = Game()
    game.player()
    ghost = game.ghost(across=2, up=2)
    ghost._cool = TOUCH_COOLDOWN
    ghost.update(game.world, dt=0.1)
    assert ghost._cool == pytest.approx(TOUCH_COOLDOWN - 0.1)


def test_burst_is_not_restarted_by_a_second_call():
    game = Game()
    coin = game.coin(across=1, up=1)
    coin.burst()
    coin.update(game.world, dt=1 / 60)
    frames = coin._bursting
    coin.burst()
    assert coin._bursting == frames


# ---- win rules ------------------------------------------------------------
def test_collected_all():
    game = Game()
    game.player()
    coin = game.coin(across=1, up=1)
    check = game.collected_all("coin")
    assert not check(game.world, 0)
    coin.remove()
    assert check(game.world, 0)


def test_score_reaches():
    game = Game()
    check = game.score_reaches(3)
    assert not check(game.world, 0)
    game.score = 3
    assert check(game.world, 0)


def test_survived_starts_counting_on_first_check():
    game = Game()
    check = game.survived(5)
    assert not check(game.world, 100.0)
    assert check(game.world, 106.0)


# ---- levels ---------------------------------------------------------------
def test_next_level_loads_the_next_picture():
    game = Game(cells=3)
    game.player()
    game.levels("###\n#@#\n###", "###\n#c#\n###")
    assert game.world.level_number == 1
    assert game.next_level() is True
    assert game.world.level_number == 2
    assert game.next_level() is False


# ---- hearts: extra lives that appear as you play --------------------------
def test_free_square_finds_an_empty_one():
    game = Game(cells=4)
    game.player(across=0, up=0)
    spot = game.free_square()
    assert spot is not None
    assert game.is_free(*spot)


def test_is_free_says_no_when_a_wall_is_there():
    game = Game(cells=4)
    game.wall(across=2, up=2)
    assert not game.is_free(2, 2)
    assert game.is_free(1, 1)


def test_free_square_returns_none_when_the_board_is_full():
    game = Game(cells=4)
    for a in range(4):
        for u in range(4):
            game.wall(across=a, up=u)
    assert game.free_square() is None


def test_hearts_places_no_more_than_the_number_asked_for():
    game = Game(cells=8)
    game.player(across=0, up=0)
    game.hearts(2, every=5)
    sprinkle = game._spawners[-1][1]
    for _ in range(6):
        sprinkle()
    assert len(game.world.alive_things("heart")) == 2


def test_hearts_never_lands_inside_a_wall():
    game = Game(cells=5)
    game.player(across=0, up=0)
    game.border()
    game.hearts(4, every=1)
    sprinkle = game._spawners[-1][1]
    for _ in range(20):
        sprinkle()
    walls = game.world.alive_things("wall")
    for heart in game.world.alive_things("heart"):
        assert not any(heart.touches(w) for w in walls)


def test_hearts_zero_adds_nothing():
    game = Game(cells=8)
    game.player()
    before = len(game._spawners)
    game.hearts(0)
    assert len(game._spawners) == before


def test_negative_hearts_is_a_friendly_error():
    game = Game()
    with pytest.raises(GameError) as e:
        game.hearts(-1)
    assert "game.hearts(3)" in str(e.value)


def test_heart_budget_refills_on_restart():
    game = Game(cells=8)
    game.player()
    game.hearts(3)
    game._heart_budget = 0
    game._reset_extras()
    assert game._heart_budget == 3


def test_falling_hearts_start_above_the_screen():
    game = Game(cells=8)
    game.player()
    game.hearts(1, move="falls")
    game._spawners[-1][1]()
    heart = game.world.alive_things("heart")[0]
    assert heart.move == "falls"
    assert heart.y < 0


# ---- every game gives the same experience --------------------------------
@pytest.mark.parametrize("name", gamebricks.GAMES)
def test_every_game_offers_extra_lives(name):
    game = gamebricks.load(name)
    assert game._heart_plan is not None, f"{name} has no game.hearts(...) line"
    assert game._heart_plan[0] > 0


@pytest.mark.parametrize("name", gamebricks.GAMES)
def test_every_game_has_a_way_to_win(name):
    game = gamebricks.load(name)
    # either one win rule, or levels ending in a door that finishes the game
    assert game._win_check is not None or game._level_texts


@pytest.mark.parametrize("name", gamebricks.GAMES)
def test_every_game_starts_with_three_lives(name):
    assert gamebricks.load(name).lives == 3


@pytest.mark.parametrize("name", gamebricks.GAMES)
def test_every_game_can_be_lost(name):
    """Something in each game has to be able to take a life away."""
    game = gamebricks.load(name)
    names = {t.name for t in game.world.things}
    losable = (
        bool(names & {"ghost", "spike"})
        or bool(game._miss_rules)
        or game.world.gravity_on
    )  # you can fall off
    assert losable


# ---- ready-made games ----------------------------------------------------
@pytest.mark.parametrize("name", gamebricks.GAMES)
def test_every_builtin_game_builds(name):
    game = gamebricks.load(name)
    assert game.world.player is not None
    assert len(game.world.things) > 1


# ---- the command line ----------------------------------------------------
def test_help_runs_and_lists_the_games(capsys):
    from gamebricks.__main__ import main

    assert main([]) == 0
    out = capsys.readouterr().out
    for name in gamebricks.GAMES:
        assert name in out


def test_list_command(capsys):
    from gamebricks.__main__ import main

    assert main(["list"]) == 0
    assert "maze" in capsys.readouterr().out


def test_unknown_command_is_friendly(capsys):
    from gamebricks.__main__ import main

    assert main(["mazee"]) == 1
    assert "Try one of these" in capsys.readouterr().out


def test_examples_are_findable_for_copying():
    from gamebricks.__main__ import _examples_dir

    folder = _examples_dir()
    assert folder is not None, "the example .py files must ship with the package"
    assert (folder / "01_my_first_game.py").exists()


def test_copy_puts_the_games_where_the_kid_is(tmp_path, monkeypatch, capsys):
    from gamebricks.__main__ import main

    monkeypatch.chdir(tmp_path)
    assert main(["copy"]) == 0
    copied = sorted(p.name for p in (tmp_path / "my-gamebricks-games").glob("*.py"))
    assert "01_my_first_game.py" in copied
    assert len(copied) >= 7


def test_new_writes_a_starter_game(tmp_path, monkeypatch, capsys):
    from gamebricks.__main__ import main

    monkeypatch.chdir(tmp_path)
    assert main(["new", "my_game.py"]) == 0
    text = (tmp_path / "my_game.py").read_text()
    assert "from gamebricks import Game" in text
    assert "game.start()" in text


def test_new_adds_the_py_ending_for_you(tmp_path, monkeypatch, capsys):
    from gamebricks.__main__ import main

    monkeypatch.chdir(tmp_path)
    main(["new", "dragons"])
    assert (tmp_path / "dragons.py").exists()


def test_new_refuses_to_clobber_an_existing_file(tmp_path, monkeypatch, capsys):
    from gamebricks.__main__ import main

    monkeypatch.chdir(tmp_path)
    (tmp_path / "my_game.py").write_text("# mine\n")
    assert main(["new", "my_game.py"]) == 1
    assert (tmp_path / "my_game.py").read_text() == "# mine\n"


def test_the_starter_game_is_valid_python():
    import ast
    from gamebricks.__main__ import STARTER

    ast.parse(STARTER)


def test_copy_never_overwrites_a_kids_edits(tmp_path, monkeypatch, capsys):
    from gamebricks.__main__ import main

    monkeypatch.chdir(tmp_path)
    main(["copy"])
    mine = tmp_path / "my-gamebricks-games" / "01_my_first_game.py"
    mine.write_text("# my own version\n")
    main(["copy"])
    assert mine.read_text() == "# my own version\n"


def test_unknown_builtin_game_is_friendly():
    with pytest.raises(GameError) as e:
        gamebricks.load("mazee")
    assert "maze" in str(e.value)
