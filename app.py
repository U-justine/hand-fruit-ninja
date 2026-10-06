"""Streamlit entry point: Hand Fruit Ninja (game screen only).

The webcam is captured in the browser via streamlit-webrtc; frames are processed
server-side with MediaPipe + the game engine and streamed back.
"""

import av
import cv2
import streamlit as st
from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, webrtc_streamer

from fruit_ninja.game import Game
from fruit_ninja.hand_tracker import HandTracker
from fruit_ninja.renderer import draw

# --- Screen settings -------------------------------------------------------
CAMERA_SIZE = (1280, 720)   # requested camera resolution (16:9). Use (640, 480) if it lags.
FIT = "contain"             # "contain": whole game visible | "cover": fills screen, crops edges
CONTROLS_HEIGHT = 70        # px reserved for the START/STOP bar under the video
# ---------------------------------------------------------------------------

RTC_CONFIG = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


class FruitNinjaProcessor(VideoProcessorBase):
    def __init__(self):
        self._tracker = HandTracker()
        self._game: Game | None = None

    def recv(self, frame):
        img = cv2.flip(frame.to_ndarray(format="bgr24"), 1)  # mirror view
        h, w = img.shape[:2]
        tip = self._tracker.process(img)
        if self._game is None:
            self._game = Game(w, h)
        self._game.update(tip)
        return av.VideoFrame.from_ndarray(draw(img, self._game), format="bgr24")


st.set_page_config(
    page_title="Hand Fruit Ninja",
    page_icon="🍉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Game screen only: hide Streamlit chrome and make the game fill the window
st.markdown(
    """
    <style>
      #MainMenu, header, footer, [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stSidebar"] {display: none !important;}
      html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
        background: #0b0b12 !important;
        overflow: hidden !important;
      }
      .block-container {padding: 0 !important; max-width: 100% !important;}
      [data-testid="stElementContainer"], [data-testid="stVerticalBlock"] {gap: 0 !important;}
      /* The webcam component lives in an iframe: stretch it to the window height */
      iframe {height: 100vh !important; height: 100dvh !important; border: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

webrtc_streamer(
    key="fruit-ninja",
    video_processor_factory=FruitNinjaProcessor,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "video": {"width": {"ideal": CAMERA_SIZE[0]}, "height": {"ideal": CAMERA_SIZE[1]}},
        "audio": False,
    },
    video_html_attrs={
        "style": {
            "width": "100%",
            "height": f"calc(100vh - {CONTROLS_HEIGHT}px)",  # vh = the iframe's height here
            "objectFit": FIT,
            "background": "#000",
            "borderRadius": "12px",
        },
        "controls": False,
        "autoPlay": True,
        "muted": True,
    },
    async_processing=True,
)