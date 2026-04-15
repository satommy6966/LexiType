# LexiType

中文说明 | English below

LexiType 是一个运行在 macOS 上的本地桌面背词输入练习 MVP，基于 Python 3.11+ 和 PySide6 构建。

LexiType is a minimal local desktop MVP for typing-based vocabulary practice on macOS, built with Python 3.11+ and PySide6.

## 项目特性 | Features

- 内置默认词库
- 支持导入本地词汇文件，内容为英文单词或词组加中文释义
- 每个导入文件都会保存为可复用的本地词书
- 可以在应用内切换多个已保存词书
- 显示当前目标单词对应的中文释义
- 可直接在单词区域输入，支持 `net worth` 这样的空格短语
- 输入完整长度后自动切换到下一项
- 错误字母会原位标红，不需要额外点击提交
- 显示当前练习进度
- 支持完成后重新开始
- Built-in default vocabulary list
- Import local vocabulary files with English words or phrases and Chinese meanings
- Save each imported file as a reusable local wordbook
- Switch between multiple saved wordbooks inside the app
- Show the Chinese meaning for the current target word
- Type directly in the word area, including phrases with spaces such as `net worth`
- Advance automatically when the full target is typed
- Highlight wrong letters in red without a separate submit step
- Show progress through the session
- Restart after completion

## 环境要求 | Requirements

- Python 3.11 或更高版本
- Python 3.11 or newer

## 安装 | Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行 | Run

```bash
python3 main.py
```

## 打包 macOS 应用 | Build macOS App

使用 PyInstaller 构建本地 macOS `.app` 应用包：

Build a local macOS `.app` bundle with PyInstaller:

```bash
source .venv/bin/activate
pip install pyinstaller
pyinstaller --windowed --name LexiType main.py
```

构建完成后，应用包会输出到：

After the build finishes, the app bundle will be here:

```bash
dist/LexiType.app
```

如果需要发布 DMG，请在本地打包流程完成后生成：

If you want to distribute a DMG, generate it after the local app build finishes:

```bash
dist/LexiType.dmg
```

说明 | Notes:

- 导入的词书会存储在 `~/Library/Application Support/LexiType/wordbooks.json`
- 如果应用未签名，在另一台 Mac 上首次打开时可能需要移除 Gatekeeper quarantine
- Imported wordbooks are stored in `~/Library/Application Support/LexiType/wordbooks.json`
- On another Mac, you may need to remove Gatekeeper quarantine the first time if the app is unsigned

## 导入词汇 | Import Vocabulary

点击应用中的 `Import`，选择本地 `.txt` 或 `.csv` 文件。

Click `Import` in the app and choose a local `.txt` or `.csv` file.

导入后，该文件会自动保存为本地词书。下次打开 LexiType 时，你可以直接在词书选择器中切换，无需再次导入。

After import, the file is automatically saved as a local wordbook. The next time you open LexiType, you can choose it directly from the wordbook selector without importing it again.

每行一个词条，支持以下格式之一：

Use one vocabulary item per line in one of these formats:

```text
abandon	放弃；抛弃
abate|减弱；缓和
aberrant,异常的
abhor;厌恶
abolish  废除
```

规则 | Rules:

- 左侧是英文单词或词组
- 右侧是中文释义
- 可使用 `Tab`、`|`、`,`、`;` 或至少两个空格分隔
- 英文内容可以是单个单词，也可以是 `net worth` 这样的短语
- 空行会被忽略
- 以 `#` 开头的行会被忽略
- 文件应保存为 UTF-8 编码
- The left side is the English word or phrase
- The right side is the Chinese meaning
- You can separate the two parts with `Tab`, `|`, `,`, `;`, or at least two spaces
- English entries may be single words or phrases such as `net worth`
- Empty lines are ignored
- Lines starting with `#` are ignored
- The file should be saved as UTF-8

## 补充说明 | Notes

- 如果没有导入任何文件，应用会使用内置默认词书
- 当前版本中的导入词书也会保存在项目根目录的 `wordbooks.json` 默认数据文件中
- 这个 MVP 不包含联网、音频、账号或云同步功能
- If no file is imported yet, the app uses the built-in default wordbook
- The repository also includes `wordbooks.json` as bundled default data
- This MVP does not include networking, audio, accounts, or cloud features
