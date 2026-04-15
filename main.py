import json
import re
import sys
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


DEFAULT_VOCABULARY = [
    ("abandon", "放弃；抛弃"),
    ("abate", "减弱；缓和"),
    ("aberrant", "异常的"),
    ("abhor", "厌恶"),
    ("abolish", "废除"),
]

WORDBOOKS_PATH = Path(__file__).with_name("wordbooks.json")


def chars_match(typed_char: str, target_char: str) -> bool:
    if typed_char.isalpha() and target_char.isalpha():
        return typed_char.lower() == target_char.lower()
    return typed_char == target_char


class TypingCanvas(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.tokens: list[str] = []
        self.meanings: list[str] = []
        self.char_entries: list[dict] = []
        self.cursor_position = 0
        self.active_token_index = 0
        self.token_char_ranges: list[tuple[int, int]] = []
        self.token_positions: list[tuple[int, int, int]] = []
        self.scroll_offset = 0
        self.font_main = QFont("Menlo", 29, QFont.Weight.Bold)
        self.font_meaning = QFont("PingFang SC", 14, QFont.Weight.Medium)
        self.line_step = 0
        self.line_tops: list[int] = []
        self.row_height = 0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(320)

    def set_state(
        self,
        tokens: list[str],
        meanings: list[str],
        char_entries: list[dict],
        cursor_position: int,
        active_token_index: int,
        token_char_ranges: list[tuple[int, int]],
    ) -> None:
        self.tokens = tokens
        self.meanings = meanings
        self.char_entries = char_entries
        self.cursor_position = cursor_position
        self.active_token_index = active_token_index
        self.token_char_ranges = token_char_ranges
        self.relayout()
        self.center_active_token()
        self.update()

    def relayout(self) -> None:
        metrics = QFontMetrics(self.font_main)
        meaning_metrics = QFontMetrics(self.font_meaning)
        left = 8
        top = 8
        token_gap = 34
        line_gap = 44
        usable_width = max(self.width() - left * 2, 200)
        self.row_height = metrics.height() + meaning_metrics.height() + 18
        self.line_step = self.row_height + (line_gap - 18)

        x = left
        y = top + metrics.ascent()
        self.token_positions = []
        self.line_tops = [top]

        for token in self.tokens:
            token_width = metrics.horizontalAdvance(token)
            if x > left and x + token_width > left + usable_width:
                x = left
                y += self.line_step
                self.line_tops.append(y - metrics.ascent())
            self.token_positions.append((x, y, token_width))
            x += token_width + token_gap

    def center_active_token(self) -> None:
        if not self.token_positions:
            self.scroll_offset = 0
            return

        index = min(self.active_token_index, len(self.token_positions) - 1)
        metrics = QFontMetrics(self.font_main)
        baseline_y = self.token_positions[index][1]
        line_top = baseline_y - metrics.ascent()
        content_bottom = (
            self.token_positions[-1][1]
            - metrics.ascent()
            + self.row_height
        )
        max_scroll = max(0, content_bottom - self.height())
        if self.line_step <= 0:
            self.scroll_offset = max(0, min(line_top, max_scroll))
            return

        # 当前整行块在视口中的上下边界。
        visible_top = line_top - self.scroll_offset
        visible_bottom = visible_top + self.row_height

        # 希望屏幕里先累积 3-4 行，再翻到下一屏。
        # 这里把触发线固定在第 4 行附近；只有当当前整行块会被裁掉时才翻。
        trigger_lines_before_scroll = 3
        desired_scroll = self.scroll_offset

        safe_top = 0
        safe_bottom = self.height()

        if visible_top < safe_top:
            row_index = max((line_top - self.line_tops[0]) // self.line_step, 0)
            desired_top_row = max(row_index - trigger_lines_before_scroll, 0)
            desired_scroll = desired_top_row * self.line_step
        elif visible_bottom > safe_bottom:
            row_index = max((line_top - self.line_tops[0]) // self.line_step, 0)
            desired_top_row = max(row_index - trigger_lines_before_scroll, 0)
            desired_scroll = desired_top_row * self.line_step

            # 如果按“前面保留 3 行”计算后，这一整行仍然放不下，就继续整行下推，
            # 直到当前整行块完全进入可视区域。
            while (
                line_top - desired_scroll + self.row_height > safe_bottom
                and desired_scroll < max_scroll
            ):
                desired_scroll += self.line_step

        self.scroll_offset = max(0, min(desired_scroll, max_scroll))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.relayout()
        self.center_active_token()

    def draw_token(
        self,
        painter: QPainter,
        metrics: QFontMetrics,
        token: str,
        token_index: int,
        x: int,
        y: int,
    ) -> None:
        colors = {
            0: QColor("#ff6b6b"),
            1: QColor("#d1d0c5"),
            2: QColor("#646669"),
        }
        cursor_color = QColor("#e2b714")

        start, end = self.token_char_ranges[token_index]
        cursor_x = x

        for char_offset, char in enumerate(token):
            entry = self.char_entries[start + char_offset]
            painter.setPen(colors[entry["flag"]])
            painter.drawText(cursor_x, y, char)
            cursor_x += metrics.horizontalAdvance(char)

        if self.active_token_index == token_index and self.cursor_position < len(self.char_entries):
            caret_index = min(self.cursor_position, end) - start
            if 0 <= caret_index < len(token):
                caret_x = x
                for char in token[:caret_index]:
                    caret_x += metrics.horizontalAdvance(char)
                char_width = metrics.horizontalAdvance(token[caret_index])
                pen = QPen(cursor_color, 2)
                painter.setPen(pen)
                painter.drawLine(
                    caret_x,
                    y + 8,
                    caret_x + max(char_width - 2, 8),
                    y + 8,
                )

    def draw_meaning(
        self,
        painter: QPainter,
        x: int,
        baseline_y: int,
        token_width: int,
        meaning: str,
        is_active: bool,
    ) -> None:
        painter.save()
        painter.setFont(self.font_meaning)
        meaning_metrics = QFontMetrics(self.font_meaning)
        color = QColor("#e2b714") if is_active else QColor("#8f7a2c")
        painter.setPen(color)
        meaning_width = meaning_metrics.horizontalAdvance(meaning)
        meaning_x = x + max((token_width - meaning_width) // 2, 0)
        meaning_y = baseline_y + meaning_metrics.ascent() + 18
        painter.drawText(meaning_x, meaning_y - self.scroll_offset, meaning)
        painter.restore()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setFont(self.font_main)
        metrics = QFontMetrics(self.font_main)

        for index, (token, (x, baseline_y, token_width)) in enumerate(
            zip(self.tokens, self.token_positions)
        ):
            line_top = baseline_y - metrics.ascent() - self.scroll_offset
            line_bottom = line_top + self.row_height
            draw_y = baseline_y - self.scroll_offset
            if line_bottom < 0 or line_top > self.height():
                continue
            self.draw_token(painter, metrics, token, index, x, draw_y)
            if index < len(self.meanings):
                self.draw_meaning(
                    painter,
                    x,
                    baseline_y,
                    token_width,
                    self.meanings[index],
                    index == self.active_token_index,
                )


class LexiTypeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LexiType")
        self.setFocusPolicy(Qt.StrongFocus)

        self.wordbooks = self.load_wordbooks()
        self.active_wordbook_name = self.load_selected_wordbook_name()
        if self.active_wordbook_name not in self.wordbooks:
            self.active_wordbook_name = next(iter(self.wordbooks))

        self.vocabulary = list(self.wordbooks[self.active_wordbook_name])

        self.tokens: list[str] = []
        self.char_array_a: list[dict] = []
        self.char_array_b: list[str] = []
        self.token_char_ranges: list[tuple[int, int]] = []
        self.cursor_position = 0
        self.active_token_index = 0
        self.session_complete = False

        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("font-size: 18px; color: #e2b714;")

        self.wordbook_selector = QComboBox()
        self.wordbook_selector.currentTextChanged.connect(self.change_wordbook)
        self.wordbook_selector.setStyleSheet(
            """
            QComboBox {
                background: #3a3c40;
                color: #d1d0c5;
                border: 1px solid #646669;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 16px;
                min-width: 220px;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                background: #323437;
                color: #d1d0c5;
                border: 1px solid #646669;
                selection-background-color: #e2b714;
                selection-color: #323437;
            }
            """
        )

        self.typing_canvas = TypingCanvas()

        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_vocabulary)
        self.import_button.setCursor(Qt.PointingHandCursor)
        self.import_button.setStyleSheet(self.button_style())

        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_session)
        self.restart_button.setCursor(Qt.PointingHandCursor)
        self.restart_button.setStyleSheet(self.button_style())

        self.refresh_wordbook_selector()

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.progress_label)
        top_bar.addStretch()
        top_bar.addWidget(self.wordbook_selector)

        button_row = QHBoxLayout()
        button_row.addWidget(self.import_button)
        button_row.addWidget(self.restart_button)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.setContentsMargins(56, 36, 56, 40)
        layout.setSpacing(12)
        layout.addLayout(top_bar)
        layout.addWidget(self.typing_canvas)
        layout.addLayout(button_row)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #323437;")
        self.setCentralWidget(container)

        self.resize(1280, 760)
        self.restart_session()

    @staticmethod
    def button_style() -> str:
        return """
        QPushButton {
            background: transparent;
            color: #646669;
            border: 1px solid #646669;
            border-radius: 8px;
            font-size: 18px;
            padding: 12px 22px;
        }
        QPushButton:hover {
            color: #d1d0c5;
            border-color: #d1d0c5;
        }
        """

    @staticmethod
    def default_wordbooks() -> dict[str, list[tuple[str, str]]]:
        return {"Default": list(DEFAULT_VOCABULARY)}

    @classmethod
    def load_wordbooks(cls) -> dict[str, list[tuple[str, str]]]:
        if not WORDBOOKS_PATH.exists():
            return cls.default_wordbooks()

        try:
            payload = json.loads(WORDBOOKS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls.default_wordbooks()

        wordbooks = payload.get("wordbooks", {})
        parsed: dict[str, list[tuple[str, str]]] = {}
        for name, entries in wordbooks.items():
            if not isinstance(name, str) or not isinstance(entries, list):
                continue
            cleaned_entries = []
            for entry in entries:
                if (
                    isinstance(entry, list)
                    and len(entry) == 2
                    and isinstance(entry[0], str)
                    and isinstance(entry[1], str)
                    and entry[0]
                    and entry[1]
                ):
                    cleaned_entries.append((entry[0], entry[1]))
            if cleaned_entries:
                parsed[name] = cleaned_entries
        return parsed or cls.default_wordbooks()

    def load_selected_wordbook_name(self) -> str:
        if not WORDBOOKS_PATH.exists():
            return "Default"
        try:
            payload = json.loads(WORDBOOKS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "Default"
        selected = payload.get("selected_wordbook")
        return selected if isinstance(selected, str) else "Default"

    def save_wordbooks(self) -> None:
        payload = {
            "selected_wordbook": self.active_wordbook_name,
            "wordbooks": {
                name: [[word, meaning] for word, meaning in entries]
                for name, entries in self.wordbooks.items()
            },
        }
        WORDBOOKS_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def refresh_wordbook_selector(self) -> None:
        with QSignalBlocker(self.wordbook_selector):
            self.wordbook_selector.clear()
            self.wordbook_selector.addItems(self.wordbooks.keys())
            self.wordbook_selector.setCurrentText(self.active_wordbook_name)

    @staticmethod
    def parse_vocabulary_file(file_path: str) -> list[tuple[str, str]]:
        items = []
        for raw_line in Path(file_path).read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = None
            for separator in ("\t", "|", ",", ";"):
                if separator in line:
                    parts = [part.strip() for part in line.split(separator, 1)]
                    break

            if parts is None:
                whitespace_parts = re.split(r"\s{2,}", line, maxsplit=1)
                if len(whitespace_parts) == 2:
                    parts = [part.strip() for part in whitespace_parts]

            if not parts or len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError(f"Invalid line: {raw_line}")

            items.append((parts[0], parts[1]))

        if not items:
            raise ValueError("Vocabulary file is empty.")
        return items

    @staticmethod
    def make_unique_wordbook_name(existing_names: set[str], base_name: str) -> str:
        if base_name not in existing_names:
            return base_name
        suffix = 2
        while f"{base_name} ({suffix})" in existing_names:
            suffix += 1
        return f"{base_name} ({suffix})"

    def rebuild_arrays(self) -> None:
        self.tokens = [word for word, _ in self.vocabulary]
        self.char_array_a = []
        self.token_char_ranges = []

        current_index = 0
        for token_index, token in enumerate(self.tokens):
            start = current_index
            for char in token:
                self.char_array_a.append(
                    {
                        "char": char,
                        "flag": 2,
                        "token_index": token_index,
                    }
                )
                current_index += 1

            end = current_index
            self.token_char_ranges.append((start, end))

            if token_index < len(self.tokens) - 1:
                self.char_array_a.append(
                    {
                        "char": " ",
                        "flag": 2,
                        "token_index": token_index,
                    }
                )
                current_index += 1

        self.char_array_b = [""] * len(self.char_array_a)
        self.cursor_position = 0
        self.active_token_index = 0
        self.session_complete = len(self.char_array_a) == 0

    def update_active_token_index(self) -> None:
        if not self.char_array_a:
            self.active_token_index = 0
            return

        position = min(self.cursor_position, len(self.char_array_a) - 1)
        self.active_token_index = self.char_array_a[position]["token_index"]

    def update_view(self) -> None:
        total_tokens = len(self.tokens)
        typed_length = sum(1 for char in self.char_array_b if char != "")
        self.session_complete = bool(self.char_array_a) and typed_length == len(self.char_array_a)
        if total_tokens == 0:
            self.progress_label.setText("0 / 0")
        elif self.session_complete:
            self.progress_label.setText(f"{total_tokens} / {total_tokens}")
        else:
            self.update_active_token_index()
            self.progress_label.setText(
                f"{self.active_token_index + 1} / {total_tokens}"
            )

        self.typing_canvas.set_state(
            self.tokens,
            [meaning for _, meaning in self.vocabulary],
            self.char_array_a,
            self.cursor_position,
            self.active_token_index,
            self.token_char_ranges,
        )
        self.setFocus()

    def restart_session(self) -> None:
        self.rebuild_arrays()
        self.update_view()

    def import_vocabulary(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Vocabulary",
            "",
            "Text Files (*.txt *.csv);;All Files (*)",
        )
        if not file_path:
            self.setFocus()
            return

        try:
            imported = self.parse_vocabulary_file(file_path)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            QMessageBox.warning(
                self,
                "Import Failed",
                "Unable to load vocabulary file.\n"
                "Use one item per line: english<TAB>中文, english|中文, english,中文, english;中文, or english  中文.\n\n"
                f"Details: {exc}",
            )
            self.setFocus()
            return

        base_name = Path(file_path).stem or "Imported"
        wordbook_name = self.make_unique_wordbook_name(
            set(self.wordbooks.keys()), base_name
        )
        self.wordbooks[wordbook_name] = imported
        self.active_wordbook_name = wordbook_name
        self.vocabulary = list(imported)
        self.save_wordbooks()
        self.refresh_wordbook_selector()
        self.restart_session()

    def change_wordbook(self, name: str) -> None:
        if not name or name == self.active_wordbook_name or name not in self.wordbooks:
            return
        self.active_wordbook_name = name
        self.vocabulary = list(self.wordbooks[name])
        self.save_wordbooks()
        self.restart_session()

    def handle_input_character(self, typed_char: str) -> None:
        if self.session_complete or self.cursor_position >= len(self.char_array_a):
            return

        self.char_array_b[self.cursor_position] = typed_char
        target_char = self.char_array_a[self.cursor_position]["char"]
        self.char_array_a[self.cursor_position]["flag"] = (
            1 if chars_match(typed_char, target_char) else 0
        )
        self.cursor_position += 1
        self.update_view()
        if self.session_complete:
            QMessageBox.information(self, "LexiType", "打字完成")

    def handle_backspace(self) -> None:
        if self.session_complete or self.cursor_position <= 0:
            return

        self.cursor_position -= 1
        self.char_array_b[self.cursor_position] = ""
        self.char_array_a[self.cursor_position]["flag"] = 2
        self.update_view()

    def keyPressEvent(self, event) -> None:
        if not self.char_array_a:
            super().keyPressEvent(event)
            return

        if self.session_complete:
            if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
                self.restart_session()
            return

        if event.key() == Qt.Key_Backspace:
            self.handle_backspace()
            return

        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            return

        text = event.text()
        if text and text.isprintable():
            self.handle_input_character(text)
            return

        super().keyPressEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = LexiTypeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
