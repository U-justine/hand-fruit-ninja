import random

import numpy as np

from fruit_ninja import renderer, sprites
from fruit_ninja.config import FRUIT_KINDS, GameConfig
from fruit_ninja.entities import Fruit
from fruit_ninja.game import Game, point_segment_distance

# No random spawns during tests
CFG = GameConfig(start_spawn_interval=10**9, min_spawn_interval=10**9)


def make_game():
    return Game(640, 480, CFG, random.Random(1))


def place(game, x, y, bomb=False):
    f = Fruit(640, 480, random.Random(2), CFG)
    f.x, f.y, f.vx, f.vy, f.radius = x, y, 0, 0, 30
    f.is_bomb = bomb
    f.kind = "bomb" if bomb else "apple"
    game.fruits.append(f)
    return f


def test_segment_distance():
    assert point_segment_distance(5, 5, (0, 0), (10, 0)) == 5
    assert point_segment_distance(15, 0, (0, 0), (10, 0)) == 5
    assert point_segment_distance(3, 4, (0, 0), (0, 0)) == 5


def test_slicing_fruit_scores_and_splits():
    g = make_game()
    f = place(g, 100, 100)
    g.update((100, 100))
    assert g.score == 1 and g.best == 1
    assert f.sliced and len(f.halves) == 2


def test_fast_swipe_does_not_skip_fruit():
    g = make_game()
    g.update((0, 100))
    place(g, 300, 100)
    g.update((600, 100))  # tip jumps over the fruit in one frame
    assert g.score == 1


def test_missing_hand_does_nothing():
    g = make_game()
    place(g, 100, 100)
    g.update(None)
    assert g.score == 0


def test_bomb_costs_life_and_ends_game():
    g = make_game()
    for _ in range(3):
        place(g, 100, 100, bomb=True)
        g.update((100, 100))
        g.update(None)
    assert g.lives == 0 and g.game_over


def test_slice_restart_target_after_game_over():
    g = make_game()
    g.score, g.best = 5, 5
    g.game_over = True
    rx, ry = g.restart_pos
    g.update((rx, ry))                 # too early: grace period
    assert g.game_over
    g.over_ticks = CFG.restart_grace_frames + 1
    g.update(None)
    g.update((rx - 20, ry))
    g.update((rx + 20, ry))
    assert not g.game_over and g.score == 0 and g.lives == CFG.lives
    assert g.best == 5                 # best score survives restart


def test_offscreen_fruit_removed():
    g = make_game()
    f = place(g, 100, 600)
    f.vy = 5
    g.update(None)
    assert not g.fruits


def test_all_sprites_load_and_render():
    for name in FRUIT_KINDS + ["bomb", "heart"]:
        assert sprites.get(name, 64).shape == (64, 64, 4)
    g = Game(640, 480, rng=random.Random(3))
    frame = np.zeros((480, 640, 3), np.uint8)
    for i in range(300):
        g.update(((i * 7) % 640, 240))
        renderer.draw(frame, g)
    g.game_over = True
    renderer.draw(frame, g)
