"""Game objects: fruits, bombs, sliced halves and juice particles."""

import random
from dataclasses import dataclass

from .config import BOMB_SPARK, DEFAULT_CONFIG, FRUIT_KINDS, JUICE, GameConfig


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple
    life: int = 25

    def step(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4
        self.life -= 1


@dataclass
class Half:
    """One half of a sliced fruit, flying apart."""
    x: float
    y: float
    vx: float
    vy: float
    angle: float
    spin: float
    side: int          # 0 = left half, 1 = right half
    gravity: float
    life: int = 45

    def step(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.spin
        self.life -= 1


class Fruit:
    """A fruit or bomb launched from the bottom of the frame."""

    def __init__(self, frame_w: int, frame_h: int,
                 rng: random.Random | None = None,
                 cfg: GameConfig = DEFAULT_CONFIG,
                 scale: float = 1.0):
        rng = rng or random
        self._rng = rng
        self.scale = scale
        self.is_bomb = rng.random() < cfg.bomb_chance
        self.kind = "bomb" if self.is_bomb else rng.choice(FRUIT_KINDS)
        self.radius = int((38 if self.is_bomb else rng.randint(32, 46)) * scale)
        self.x = float(rng.randint(int(frame_w * 0.15), int(frame_w * 0.85)))
        self.y = float(frame_h + self.radius)
        self.vx = rng.uniform(-3, 3) * scale
        self.vy = rng.uniform(-18, -13) * scale
        self.gravity = cfg.gravity * scale
        self.angle = rng.uniform(0, 360)
        self.spin = rng.uniform(-4, 4)
        self.sliced = False
        self.halves: list[Half] = []
        self.particles: list[Particle] = []

    def step(self) -> None:
        if not self.sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            self.angle += self.spin
        for h in self.halves:
            h.step()
        for p in self.particles:
            p.step()
        self.halves = [h for h in self.halves if h.life > 0]
        self.particles = [p for p in self.particles if p.life > 0]

    def slice(self) -> None:
        self.sliced = True
        r, s = self._rng, self.scale
        if self.is_bomb:
            color, count = BOMB_SPARK, 26
        else:
            color, count = JUICE[self.kind], 16
            for side, direction in ((0, -1), (1, 1)):
                self.halves.append(Half(
                    x=self.x + direction * self.radius * 0.5, y=self.y,
                    vx=self.vx + direction * 3 * s, vy=self.vy * 0.3,
                    angle=self.angle, spin=direction * r.uniform(3, 7),
                    side=side, gravity=self.gravity))
        self.particles = [
            Particle(self.x, self.y, r.uniform(-7, 7) * s, r.uniform(-7, 7) * s, color)
            for _ in range(count)
        ]

    def is_done(self, frame_h: int) -> bool:
        """True when it can be removed from the game."""
        if self.sliced:
            return not self.halves and not self.particles
        return self.vy > 0 and self.y > frame_h + self.radius + 50
