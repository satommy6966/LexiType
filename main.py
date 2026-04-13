import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


VOCABULARY = [
    ("abandon", "放弃；抛弃"),
    ("abate", "减弱；缓和"),
    ("aberrant", "异常的"),
    ("abhor", "厌恶"),
    ("abolish", "废除"),
]


class LexiTypeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LexiType")
        self.correct_count = 0
        self.wrong_count = 0
        self.current_index = 0
        self.current_input = ""
        self.session_complete = False
        self.setFocusPolicy(Qt.StrongFocus)

        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setStyleSheet(
            "font-size: 24px; font-weight: 600; color: #e2b714;"
        )

        self.word_label = QLabel()
        self.word_label.hide()

        self.word_list = QTextEdit()
        self.word_list.setReadOnly(True)
        self.word_list.setFrameStyle(0)
        self.word_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.word_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.word_list.setStyleSheet(
            """
            QTextEdit {
                background: transparent;
                border: none;
                color: #646669;
                font-size: 34px;
                font-weight: 700;
                selection-background-color: transparent;
            }
            """
        )
        self.word_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.status_label = QLabel(" ")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setStyleSheet("font-size: 18px; color: #e2b714;")

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignLeft)
        self.progress_label.setStyleSheet("font-size: 18px; color: #e2b714;")

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignRight)
        self.stats_label.setStyleSheet("font-size: 16px; color: #646669;")

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_answer)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(
            """
            QPushButton {
                background: #e2b714;
                color: #323437;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 700;
                padding: 12px 22px;
            }
            QPushButton:disabled {
                background: #646669;
                color: #323437;
            }
            """
        )

        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_session)
        self.restart_button.setCursor(Qt.PointingHandCursor)
        self.restart_button.setStyleSheet(
            """
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
        )

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.progress_label)
        top_bar.addStretch()
        top_bar.addWidget(self.stats_label)

        button_row = QHBoxLayout()
        button_row.addWidget(self.restart_button)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.setContentsMargins(56, 36, 56, 40)
        layout.setSpacing(18)
        layout.addLayout(top_bar)
        layout.addStretch(2)
        layout.addWidget(self.meaning_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(24)
        layout.addWidget(self.word_list)
        layout.addWidget(self.status_label)
        layout.addLayout(button_row)
        layout.addStretch(3)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #323437;")
        self.setCentralWidget(container)

        self.restart_session()
        self.resize(1100, 700)

    def current_item(self) -> tuple[str, str]:
        return VOCABULARY[self.current_index]

    @staticmethod
    def color_char(character: str, color: str) -> str:
        return f'<span style="color: {color};">{character}</span>'

    def render_word(self, index: int, word: str) -> str:
        if index < self.current_index:
            return f'<span style="color: #7a7c80;">{word}</span>'

        if index > self.current_index:
            return f'<span style="color: #646669;">{word}</span>'

        pieces = []
        for position, character in enumerate(word):
            if position < len(self.current_input):
                if self.current_input[position] == character:
                    pieces.append(self.color_char(character, "#e2b714"))
                else:
                    pieces.append(self.color_char(character, "#ff6b6b"))
            else:
                pieces.append(self.color_char(character, "#d1d0c5"))

        if len(self.current_input) > len(word):
            for character in self.current_input[len(word) :]:
                pieces.append(self.color_char(character, "#ff6b6b"))

        return "".join(pieces)

    def render_word_list(self) -> None:
        words = []
        for index, (word, _) in enumerate(VOCABULARY):
            words.append(self.render_word(index, word))
        html = (
            '<div style="line-height: 1.8;">'
            + "&nbsp;&nbsp;".join(words)
            + "</div>"
        )
        self.word_list.setHtml(html)

    def update_view(self) -> None:
        if self.current_index < len(VOCABULARY):
            _, meaning = self.current_item()
            self.meaning_label.setText(meaning)
            self.progress_label.setText(
                f"{self.current_index + 1} / {len(VOCABULARY)}"
            )
            self.submit_button.setEnabled(True)
            self.render_word_list()
        else:
            self.session_complete = True
            self.meaning_label.setText("本轮练习已完成")
            self.progress_label.setText(
                f"{len(VOCABULARY)} / {len(VOCABULARY)}"
            )
            self.submit_button.setEnabled(False)
            self.render_word_list()
            QMessageBox.information(self, "LexiType", "Completed. You can restart.")

        self.stats_label.setText(
            f"Correct {self.correct_count}   Wrong {self.wrong_count}"
        )
        self.setFocus()

    def submit_answer(self) -> None:
        if self.current_index >= len(VOCABULARY):
            return

        typed_text = self.current_input.strip()
        correct_word, _ = self.current_item()

        if typed_text == correct_word:
            self.correct_count += 1
            self.status_label.setText("Correct")
            self.status_label.setStyleSheet("font-size: 18px; color: #e2b714;")
        else:
            self.wrong_count += 1
            self.status_label.setText(f"Wrong: correct answer is {correct_word}")
            self.status_label.setStyleSheet("font-size: 18px; color: #ff6b6b;")

        self.current_index += 1
        self.current_input = ""
        self.update_view()

    def restart_session(self) -> None:
        self.correct_count = 0
        self.wrong_count = 0
        self.current_index = 0
        self.current_input = ""
        self.session_complete = False
        self.status_label.setText(" ")
        self.status_label.setStyleSheet("font-size: 18px; color: #e2b714;")
        self.submit_button.setEnabled(True)
        self.update_view()

    def keyPressEvent(self, event) -> None:
        if self.session_complete:
            if event.key() in {Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space}:
                self.restart_session()
                return
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Backspace:
            self.current_input = self.current_input[:-1]
            self.render_word_list()
            return

        if event.key() in {Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space}:
            self.submit_answer()
            return

        text = event.text()
        if text and text.isalpha():
            self.current_input += text.lower()
            self.render_word_list()
            return

        super().keyPressEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = LexiTypeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
