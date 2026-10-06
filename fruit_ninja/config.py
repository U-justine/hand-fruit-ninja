"""Tunable game settings in one place."""

from dataclasses import dataclass

# Emoji sprite name -> juice colour (BGR) used for slice splashes
JUICE = {
    "watermelon": (90, 80, 240),
    "apple": (60, 60, 230),
    "orange": (0, 140, 255),
    "lemon": (0, 230, 255),
    "banana": (0, 220, 250),
    "strawberry": (70, 60, 235),
    "grapes": (180, 70, 150),
    "pineapple": (0, 200, 250),
    "kiwi": (70, 200, 120),
    "peach": (140, 170, 255),
}
FRUIT_KINDS = list(JUICE)
BOMB_SPARK = (0, 140, 255)

REFERENCE_HEIGHT = 480  # sizes and speeds scale relative to this frame height


@dataclass(frozen=True)
class GameConfig:
    lives: int = 3
    bomb_chance: float = 0.15          # probability a spawn is a bomb
    start_spawn_interval: int = 45     # frames between spawns at start
    min_spawn_interval: int = 20       # hardest the game gets
    gravity: float = 0.6
    slice_padding: int = 14            # extra hit radius around the blade (px)
    trail_length: int = 10             # blade trail points
    smoothing: float = 0.5             # 0 = raw, closer to 1 = smoother/laggier
    restart_grace_frames: int = 30     # ignore the blade briefly after game over


DEFAULT_CONFIG = GameConfig()
