# LexiType

LexiType is a minimal local desktop MVP for typing-based vocabulary practice on macOS, built with Python 3.11+ and PySide6.

## Features

- Built-in default vocabulary list
- Import local vocabulary files with English words and Chinese meanings
- Save each imported file as a reusable local wordbook
- Switch between multiple saved wordbooks inside the app
- Shows the Chinese meaning for the current target word
- Type directly in the word area, including spaces inside phrases like `net worth`
- Each item advances automatically when you finish typing its full length
- Wrong letters turn red in place; there is no per-word submit step
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

After import, the file is automatically saved as a local wordbook. The next time you open LexiType, you can choose it directly from the wordbook selector without importing it again.

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
- English entries may be single words or phrases such as `net worth`
- Empty lines are ignored
- Lines starting with `#` are ignored
- The file should be saved as UTF-8

## Notes

- If no file is imported yet, the app uses the built-in default wordbook.
- Imported wordbooks are stored locally in `wordbooks.json`.
- This MVP does not include file import, networking, audio, accounts, or cloud features.
