# LexiType

LexiType is a minimal local desktop MVP for typing-based vocabulary practice on macOS, built with Python 3.11+ and PySide6.

## Features

- Hardcoded vocabulary list
- Shows English word and Chinese meaning
- Type the English word and submit with Enter or the button
- Tracks correct and wrong counts
- Shows progress through the session
- Lets you restart after completion

## Requirements

- Python 3.11 or newer

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

## Notes

- The vocabulary list is currently hardcoded in `main.py`.
- This MVP does not include file import, networking, audio, accounts, or cloud features.
