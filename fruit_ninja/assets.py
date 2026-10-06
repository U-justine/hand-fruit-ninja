"""
assets.py
Renders emoji characters into images with transparency.
Caches each emoji so rendering happens only once.
Falls back to a plain circle if no emoji font is found.
"""

import os
import sys
from typing import Dict, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .config import DEFAULT_CONFIG


# ---- Font discovery ----
def _find_emoji_font() -> Optional[str]:
    """Returns a path to a colour-emoji font, or None."""
    candidates = []

    if sys.platform == "win32":
        candidates += [
            "C:/Windows/Fonts/seguiemj.ttf",   # Segoe UI Emoji
            "C:/Windows/Fonts/seguisym.ttf",
        ]
    elif sys.platform == "darwin":
        candidates += [
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/Library/Fonts/Apple Color Emoji.ttc",
        ]
    else:  # Linux (e.g. Streamlit Cloud)
        candidates += [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/noto/NotoColorEmoji-Regular.ttf",
            "/usr/share/fonts/noto/NotoColorEmoji.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


_EMOJI_FONT_PATH = _find_emoji_font()


# ---- Emoji rendering ----
def _render_emoji(emoji: str, size: int = 128) -> Optional[np.ndarray]:
    """
    Renders an emoji into a BGRA numpy array (transparent background).
    Returns None if the emoji font isn't available.
    """
    if _EMOJI_FONT_PATH is None:
        return None

    try:
        font = ImageFont.truetype(_EMOJI_FONT_PATH, size=size)
    except (OSError, IOError):
        return None

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        bbox = draw.textbbox((0, 0), emoji, font=font, embedded_color=True)
    except Exception:
        return None

    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]

    try:
        draw.text((x, y), emoji, font=font, embedded_color=True)
    except Exception:
        return None

    arr = np.array(img)
    bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
    return bgra


# ---- Cache ----
_FRUIT_CACHE: Dict[str, Optional[np.ndarray]] = {}
_BOMB_CACHE: Dict[str, Optional[np.ndarray]] = {}
_EMOJI_WORKS = True


def get_fruit_sprite(name: str, size: Optional[int] = None) -> Optional[np.ndarray]:
    """Returns a BGRA sprite for the given fruit name, or None if emoji fails."""
    global _EMOJI_WORKS

    if not _EMOJI_WORKS:
        return None

    if size is None:
        size = DEFAULT_CONFIG.fruit_sprite_size

    key = f"{name}@{size}"
    if key in _FRUIT_CACHE:
        return _FRUIT_CACHE[key]

    emoji = DEFAULT_CONFIG.fruit_emojis.get(name)
    if emoji is None:
        _FRUIT_CACHE[key] = None
        return None

    sprite = _render_emoji(emoji, size=size)
    if sprite is None:
        _EMOJI_WORKS = False

    _FRUIT_CACHE[key] = sprite
    return sprite


def get_bomb_sprite(size: Optional[int] = None) -> Optional[np.ndarray]:
    """Returns a BGRA sprite for the bomb emoji, or None."""
    global _EMOJI_WORKS

    if not _EMOJI_WORKS:
        return None

    if size is None:
        size = DEFAULT_CONFIG.bomb_sprite_size

    key = f"bomb@{size}"
    if key in _BOMB_CACHE:
        return _BOMB_CACHE[key]

    sprite = _render_emoji(DEFAULT_CONFIG.bomb_emoji, size=size)
    if sprite is None:
        _EMOJI_WORKS = False

    _BOMB_CACHE[key] = sprite
    return sprite


def emoji_available() -> bool:
    """True if the emoji font was found and rendering succeeded."""
    return _EMOJI_FONT_PATH is not None and _EMOJI_WORKS


# ---- Compositing helpers ----
def overlay_sprite(bg: np.ndarray, sprite: np.ndarray, cx: int, cy: int) -> np.ndarray:
    """Alpha-blends a BGRA sprite onto a BGR background, centered at (cx, cy)."""
    if sprite is None:
        return bg

    sh, sw = sprite.shape[:2]
    bh, bw = bg.shape[:2]

    x = cx - sw // 2
    y = cy - sh // 2

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(bw, x + sw), min(bh, y + sh)
    if x1 >= x2 or y1 >= y2:
        return bg

    sx1, sy1 = x1 - x, y1 - y
    sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)

    sprite_crop = sprite[sy1:sy2, sx1:sx2]
    bg_crop = bg[y1:y2, x1:x2].astype(np.float32)

    alpha = sprite_crop[:, :, 3:4].astype(np.float32) / 255.0
    fg = sprite_crop[:, :, :3].astype(np.float32)

    bg[y1:y2, x1:x2] = (alpha * fg + (1.0 - alpha) * bg_crop).astype(np.uint8)
    return bg


def rotate_sprite(sprite: np.ndarray, angle: float) -> np.ndarray:
    """Rotates a BGRA sprite around its center."""
    if sprite is None:
        return None

    h, w = sprite.shape[:2]
    cx, cy = w / 2, h / 2

    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)
    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    rgb = sprite[:, :, :3]
    alpha = sprite[:, :, 3]

    rgb_r = cv2.warpAffine(rgb, M, (new_w, new_h),
                           flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0, 0, 0))
    a_r = cv2.warpAffine(alpha, M, (new_w, new_h),
                         flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT,
                         borderValue=0)

    return np.dstack([rgb_r, a_r])