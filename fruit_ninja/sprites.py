"""Emoji sprite loading and alpha-blending onto OpenCV frames."""

from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

ASSET_DIR = Path(__file__).parent / "assets" / "emoji"


@lru_cache(maxsize=None)
def _load(name: str) -> np.ndarray:
    img = cv2.imread(str(ASSET_DIR / f"{name}.png"), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Missing emoji sprite: {ASSET_DIR / (name + '.png')}")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 3:
        alpha = np.full(img.shape[:2] + (1,), 255, np.uint8)
        img = np.concatenate([img, alpha], axis=2)
    return img


@lru_cache(maxsize=512)
def get(name: str, size: int, dim: bool = False) -> np.ndarray:
    """Return a square BGRA sprite of `size` px (optionally greyed out)."""
    size = max(4, int(size))
    src = _load(name)
    interp = cv2.INTER_AREA if size < src.shape[0] else cv2.INTER_CUBIC
    img = cv2.resize(src, (size, size), interpolation=interp)
    if dim:
        img = img.copy()
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
        img[:, :, :3] = gray[:, :, None]
        img[:, :, 3] = (img[:, :, 3] * 0.35).astype(np.uint8)
    return img


@lru_cache(maxsize=256)
def halves(name: str, size: int):
    """Left and right halves of a sprite (for the slice animation)."""
    img = get(name, size)
    mid = img.shape[1] // 2
    return img[:, :mid].copy(), img[:, mid:].copy()


def overlay(frame: np.ndarray, sprite: np.ndarray, cx: float, cy: float,
            angle: float = 0.0) -> None:
    """Alpha-blend `sprite` centred at (cx, cy), optionally rotated, in place."""
    if angle:
        # Pad first so the corners are not clipped while rotating
        pad = int(max(sprite.shape[:2]) * 0.22)
        sprite = cv2.copyMakeBorder(sprite, pad, pad, pad, pad,
                                    cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        sh, sw = sprite.shape[:2]
        m = cv2.getRotationMatrix2D((sw / 2, sh / 2), angle, 1.0)
        sprite = cv2.warpAffine(sprite, m, (sw, sh), flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    sh, sw = sprite.shape[:2]
    x0, y0 = int(cx - sw / 2), int(cy - sh / 2)
    fh, fw = frame.shape[:2]
    x1, y1 = max(x0, 0), max(y0, 0)
    x2, y2 = min(x0 + sw, fw), min(y0 + sh, fh)
    if x1 >= x2 or y1 >= y2:
        return
    part = sprite[y1 - y0:y2 - y0, x1 - x0:x2 - x0]
    alpha = part[:, :, 3:4].astype(np.float32) / 255.0
    roi = frame[y1:y2, x1:x2]
    roi[:] = (part[:, :, :3] * alpha + roi * (1.0 - alpha)).astype(np.uint8)
