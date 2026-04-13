# LexiType

LexiType is a minimal local desktop MVP for typing-based vocabulary practice on macOS, built with Python 3.11+ and PySide6.

## Features

- Built-in default vocabulary list
- Import a local vocabulary file with English words and Chinese meanings
- Shows the Chinese meaning for the current target word
- Type directly in the word area and submit with `Space` or `Enter`
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

## Import Vocabulary

Click `Import` in the app and choose a local `.txt` or `.csv` file.

Use one vocabulary item per line in one of these formats:

```text
abandon	放弃；抛弃
abate|减弱；缓和
aberrant,异常的
abhor;厌恶
abolish  废除
```

Rules:

- Left side is the English word
- Right side is the Chinese meaning
- You can separate the two parts with `Tab`, `|`, `,`, `;`, or at least two spaces
- Empty lines are ignored
- Lines starting with `#` are ignored
- The file should be saved as UTF-8

## Notes

- If no file is imported, the app uses the built-in sample vocabulary.
- This MVP does not include file import, networking, audio, accounts, or cloud features.
