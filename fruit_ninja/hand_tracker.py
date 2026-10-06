"""MediaPipe Hands wrapper that returns a smoothed index-fingertip position."""

from typing import Optional

import cv2
import mediapipe as mp

from .config import DEFAULT_CONFIG

INDEX_TIP = 8


class HandTracker:
    def __init__(self, smoothing: float = DEFAULT_CONFIG.smoothing):
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.smoothing = smoothing
        self._last: Optional[tuple[float, float]] = None

    def process(self, frame_bgr, draw_skeleton: bool = False) -> Optional[tuple[float, float]]:
        """Return the smoothed index fingertip in pixels, or None if no hand."""
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            self._last = None
            return None

        hand = results.multi_hand_landmarks[0]
        if draw_skeleton:
            self._mp_draw.draw_landmarks(frame_bgr, hand, self._mp_hands.HAND_CONNECTIONS)

        lm = hand.landmark[INDEX_TIP]
        raw = (lm.x * w, lm.y * h)
        if self._last is None:
            self._last = raw
        else:
            s = self.smoothing
            self._last = (s * self._last[0] + (1 - s) * raw[0],
                          s * self._last[1] + (1 - s) * raw[1])
        return self._last

    def close(self) -> None:
        self._hands.close()
