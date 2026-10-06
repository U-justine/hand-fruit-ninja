"""Pure game logic. No OpenCV / MediaPipe here, so it is easy to test."""

import math
import random
from collections import deque
from typing import Optional

from .config import DEFAULT_CONFIG, REFERENCE_HEIGHT, GameConfig
from .entities import Fruit

Point = tuple[float, float]
Blade = tuple[Point, Point]


def point_segment_distance(px: float, py: float, a: Point, b: Point) -> float:
    """Shortest distance from point P to the segment A-B."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


class Game:
    def __init__(self, frame_w: int, frame_h: int,
                 cfg: GameConfig = DEFAULT_CONFIG,
                 rng: random.Random | None = None):
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.cfg = cfg
        self.rng = rng or random.Random()
        self.scale = frame_h / REFERENCE_HEIGHT
        # "Slice to play again" target shown on the game-over screen
        self.restart_pos: Point = (frame_w / 2, frame_h * 0.66)
        self.restart_radius = int(70 * self.scale)
        self.best = 0
        self.tick = 0
        self.reset()

    def reset(self) -> None:
        self.fruits: list[Fruit] = []
        self.score = 0
        self.lives = self.cfg.lives
        self.game_over = False
        self.over_ticks = 0
        self.spawn_timer = 0
        self.spawn_interval = self.cfg.start_spawn_interval
        self.trail: deque[Point] = deque(maxlen=self.cfg.trail_length)
        self._prev_tip: Optional[Point] = None

    def update(self, tip: Optional[Point]) -> None:
        """Advance one frame. `tip` is the fingertip position or None."""
        self.tick += 1
        blade = self._blade(tip)

        if self.game_over:
            self.over_ticks += 1
            for fruit in self.fruits:
                fruit.step()
            self.fruits = [f for f in self.fruits if not f.is_done(self.frame_h)]
            if blade and self.over_ticks > self.cfg.restart_grace_frames:
                rx, ry = self.restart_pos
                if point_segment_distance(rx, ry, *blade) < self.restart_radius:
                    self.reset()
            return

        self._maybe_spawn()
        for fruit in self.fruits:
            fruit.step()
            if blade and not fruit.sliced and self._hit(fruit, blade):
                self._on_slice(fruit)
        self.fruits = [f for f in self.fruits if not f.is_done(self.frame_h)]

    def _blade(self, tip: Optional[Point]) -> Optional[Blade]:
        """Segment from the last tip to this tip, so fast swipes don't skip fruit."""
        if tip is None:
            self.trail.clear()
            self._prev_tip = None
            return None
        blade = (self._prev_tip or tip, tip)
        self.trail.append(tip)
        self._prev_tip = tip
        return blade

    def _maybe_spawn(self) -> None:
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.fruits.append(
                Fruit(self.frame_w, self.frame_h, self.rng, self.cfg, self.scale))
            self.spawn_timer = 0
            self.spawn_interval = max(self.cfg.min_spawn_interval, self.spawn_interval - 1)

    def _hit(self, fruit: Fruit, blade: Blade) -> bool:
        d = point_segment_distance(fruit.x, fruit.y, *blade)
        return d < fruit.radius + self.cfg.slice_padding * self.scale

    def _on_slice(self, fruit: Fruit) -> None:
        fruit.slice()
        if fruit.is_bomb:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.over_ticks = 0
        else:
            self.score += 1
            self.best = max(self.best, self.score)
