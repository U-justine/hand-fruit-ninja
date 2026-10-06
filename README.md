# 🍉 Hand Fruit Ninja

> Slice emoji fruits in mid-air using your fingertip. Runs entirely in your browser — no install, no controller, no keyboard.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-0097A7?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎮 What It Is

A live, browser-based game where your **webcam tracks your fingertip** and you slice flying emoji fruits in real time. Miss three bombs, and you're out.

No app install. No Python. No setup. Just a link and your camera.

---

## ✨ Features

- 🖐️ **Real-time hand tracking** — MediaPipe detects your index, middle, ring, and pinky fingertips at 30 FPS
- 🍉 **Emoji fruits** — watermelon, orange, apple, banana, grape, lemon fly up from the bottom
- 💣 **Bombs** — slice one, lose a life
- ⚡ **Rising difficulty** — fruits spawn faster as your score climbs
- 💥 **Slice particles** — every fruit bursts into colored particles when cut
- 🌀 **Rotating fruits** — each fruit spins as it flies
- 📊 **Live HUD** — score and lives displayed in the corner
- 🌐 **Runs anywhere** — desktop, tablet, or phone — the webcam never leaves your device

---

## 🚀 Live Demo

👉 **[hand-fruit-ninja.streamlit.app](https://hand-fruit-ninja-aqjc7guckappkenjzzyioh6.streamlit.app/)** 

Open on any device, click **START**, allow camera access, and start slicing.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Browser webcam streaming | `streamlit-webrtc` (WebRTC) |
| Hand tracking | `mediapipe` (21 landmarks per hand) |
| Image processing | `opencv-python-headless` |
| Emoji rendering | `pillow` |
| Math & collisions | `numpy` |
| Video decoding | `av` |
| UI | `streamlit` |

---

## 📦 Run Locally

```bash
git clone https://github.com/U-justine/hand-fruit-ninja.git
cd hand-fruit-ninja

python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🌐 Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select: `U-justine/hand-fruit-ninja`, branch `main`, file `app.py`
5. Click **Deploy**

You get a public URL in ~60 seconds.

**Note:** the project includes a `packages.txt` that installs `fonts-noto-color-emoji` so emojis render correctly on Streamlit Cloud's Linux environment.

---

## 🎯 How to Play

| Action | Result |
|---|---|
| Move your index finger across the screen | Slice fruits |
| Slice a fruit | +1 point |
| Slice a bomb 💣 | −1 life |
| Lose all 3 lives | Game Over |
| Refresh the page | Play again |

**Tips:**
- Stand 2–3 feet from the camera
- Well-lit room = better detection
- Keep one hand visible at a time
- Fruits spin — timing matters

---

## 📁 Project Structure

```
hand-fruit-ninja/
├── app.py                    # Streamlit entry point
├── fruit_ninja/
│   ├── __init__.py
│   ├── assets.py             # Emoji → image rendering
│   ├── config.py             # Tunable settings
│   ├── entities.py           # Fruit, Bomb, Particle
│   ├── game.py               # Game loop and state
│   ├── hand_tracker.py       # MediaPipe wrapper
│   └── renderer.py           # Drawing + HUD
├── tests/                    # Unit tests
├── .streamlit/
│   └── config.toml           # Streamlit theme
├── packages.txt              # System deps for Streamlit Cloud
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔧 Tunable Settings

All gameplay knobs live in `fruit_ninja/config.py`:

```python
lives: int = 3
bomb_chance: float = 0.15
start_spawn_interval: int = 45
min_spawn_interval: int = 20
gravity: float = 0.6
slice_padding: int = 14
rotate_fruits: bool = True
slice_particles: int = 14
```

Change any of these and rerun — no code edits required.

---

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 📜 License

MIT — use it, remix it, share it.

---

## 🙏 Credits

Built with:
- [MediaPipe](https://mediapipe.dev) — hand tracking
- [Streamlit](https://streamlit.io) — app framework
- [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc) — browser webcam
- [OpenCV](https://opencv.org) — image processing
- [Pillow](https://python-pillow.org) — emoji rendering

Made with 🍉 in Kigali, Rwanda.

---

## 🔗 Connect

- **GitHub:** [@U-justine](https://github.com/U-justine)
- **LinkedIn:** [in/umutoni-justine](https://linkedin.com/in/umutoni-justine)
- **Email:** umutonijustine1@gmail.com
