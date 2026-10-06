"""Draws the game onto an OpenCV frame using emoji sprites."""

import math

import cv2

from . import sprites
from .game import Game

FONT = cv2.FONT_HERSHEY_DUPLEX
WHITE = (255, 255, 255)
SOFT = (210, 210, 210)
GOLD = (60, 200, 255)
CYAN = (255, 230, 90)


def put_text(frame, text, x, y, scale, color=WHITE, thick=2, center=False):
    """Text with a dark outline so it reads on any camera background."""
    if center:
        (tw, _), _ = cv2.getTextSize(text, FONT, scale, thick)
        x -= tw // 2
    org = (int(x), int(y))
    cv2.putText(frame, text, org, FONT, scale, (0, 0, 0), thick + 4, cv2.LINE_AA)
    cv2.putText(frame, text, org, FONT, scale, color, thick, cv2.LINE_AA)


def draw(frame, game: Game):
    h, w = frame.shape[:2]
    s = game.scale

    # Slightly dim the camera so the emoji pop
    cv2.convertScaleAbs(frame, dst=frame, alpha=0.78, beta=0)

    _draw_fruits(frame, game)
    _draw_blade(frame, game)
    _draw_hud(frame, game, w, s)
    if game.game_over:
        _draw_game_over(frame, game, w, h, s)
        _draw_blade(frame, game)  # keep the blade on top of the overlay
    return frame


def _draw_fruits(frame, game: Game) -> None:
    for fruit in game.fruits:
        for p in fruit.particles:
            cv2.circle(frame, (int(p.x), int(p.y)), max(2, int(5 * game.scale * p.life / 25)),
                       p.color, -1, cv2.LINE_AA)
        if fruit.sliced:
            size = fruit.radius * 2
            if fruit.halves:
                left, right = sprites.halves(fruit.kind, size)
                for half in fruit.halves:
                    sprites.overlay(frame, (left, right)[half.side], half.x, half.y, half.angle)
        else:
            sprites.overlay(frame, sprites.get(fruit.kind, fruit.radius * 2),
                            fruit.x, fruit.y, fruit.angle)


def _draw_blade(frame, game: Game) -> None:
    pts = [(int(x), int(y)) for x, y in game.trail]
    n = len(pts)
    for i in range(1, n):
        t = i / n
        cv2.line(frame, pts[i - 1], pts[i], CYAN, max(2, int(14 * game.scale * t)), cv2.LINE_AA)
        cv2.line(frame, pts[i - 1], pts[i], WHITE, max(1, int(5 * game.scale * t)), cv2.LINE_AA)
    if pts:
        cv2.circle(frame, pts[-1], int(9 * game.scale), WHITE, -1, cv2.LINE_AA)
        cv2.circle(frame, pts[-1], int(13 * game.scale), CYAN, 2, cv2.LINE_AA)


def _draw_hud(frame, game: Game, w: int, s: float) -> None:
    put_text(frame, str(game.score), 26 * s, 62 * s, 2.0 * s, WHITE, max(2, int(3 * s)))
    put_text(frame, f"BEST {game.best}", 28 * s, 92 * s, 0.6 * s, SOFT, 1)

    size = int(46 * s)
    gap = int(8 * s)
    for i in range(game.cfg.lives):
        # Right-aligned hearts; lost lives are greyed out
        x = w - int(26 * s) - size // 2 - (game.cfg.lives - 1 - i) * (size + gap)
        sprite = sprites.get("heart", size, dim=i >= game.lives)
        sprites.overlay(frame, sprite, x, int(44 * s))


def _draw_game_over(frame, game: Game, w: int, h: int, s: float) -> None:
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    put_text(frame, "GAME OVER", w / 2, h * 0.24, 2.3 * s, (80, 80, 255), max(3, int(5 * s)), True)
    put_text(frame, f"Score {game.score}", w / 2, h * 0.35, 1.3 * s, WHITE, max(2, int(3 * s)), True)
    put_text(frame, f"Best {game.best}", w / 2, h * 0.42, 0.9 * s, GOLD, 2, True)

    pulse = 1 + 0.07 * math.sin(game.tick / 6)
    rx, ry = game.restart_pos
    sprites.overlay(frame, sprites.get("watermelon", int(game.restart_radius * 2 * pulse)), rx, ry)
    put_text(frame, "SLICE TO PLAY AGAIN", w / 2, ry + game.restart_radius + 40 * s,
             0.8 * s, WHITE, 2, True)
