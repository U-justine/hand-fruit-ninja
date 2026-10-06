# 🍉 Hand Fruit Ninja

Slice emoji fruit in mid-air with your index finger. The webcam is captured in the
browser (`streamlit-webrtc`), the fingertip is tracked with MediaPipe Hands, and the
game is drawn on the live video. The page shows only the game.

## Project structure

```
hand-fruit-ninja/
├── app.py                  # Streamlit page (game screen only) + video processor
├── fruit_ninja/
│   ├── config.py           # Tunable settings, juice colours
│   ├── entities.py         # Fruit, bomb, sliced halves, particles
│   ├── game.py             # Pure game logic (scoring, spawning, slicing, restart)
│   ├── hand_tracker.py     # MediaPipe fingertip tracking + smoothing
│   ├── sprites.py          # Emoji sprite loading + alpha blending
│   ├── renderer.py         # Drawing: fruit, blade trail, HUD, game over
│   └── assets/emoji/       # Twemoji PNG sprites
├── tests/test_game.py
├── .streamlit/config.toml
├── requirements.txt
└── requirements-dev.txt
```

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501, click **START**, allow camera access. Python 3.10–3.12.

## Play

- Swipe your index finger through fruit: +1 point
- Bombs cost a heart (3 hearts)
- On game over, slice the watermelon to play again

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy (Streamlit Community Cloud)

Push to GitHub → https://share.streamlit.io → **New app** → main file `app.py`.

## Customise

Edit `fruit_ninja/config.py` (lives, bomb chance, spawn speed, blade size, smoothing).
To add a fruit, drop a PNG into `fruit_ninja/assets/emoji/` and add its name and juice
colour to `JUICE` in `config.py`.

## Credits

Emoji graphics: [Twemoji](https://github.com/jdecked/twemoji), © Twitter, Inc. and
contributors, licensed [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## License

Code: MIT.
