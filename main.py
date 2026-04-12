import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
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

        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setStyleSheet("font-size: 18px; color: #555;")

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type the English word")
        self.input_box.returnPressed.connect(self.submit_answer)

        self.status_label = QLabel(" ")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_answer)

        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_session)

        layout = QVBoxLayout()
        layout.addWidget(self.word_label)
        layout.addWidget(self.meaning_label)
        layout.addWidget(self.input_box)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.restart_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.restart_session()
        self.resize(520, 320)

    def current_item(self) -> tuple[str, str]:
        return VOCABULARY[self.current_index]

    def update_view(self) -> None:
        if self.current_index < len(VOCABULARY):
            word, meaning = self.current_item()
            self.word_label.setText(word)
            self.meaning_label.setText(meaning)
            self.progress_label.setText(
                f"Progress: {self.current_index + 1} / {len(VOCABULARY)}"
            )
            self.submit_button.setEnabled(True)
            self.input_box.setEnabled(True)
        else:
            self.word_label.setText("Session complete")
            self.meaning_label.setText("You finished all vocabulary items.")
            self.progress_label.setText(
                f"Progress: {len(VOCABULARY)} / {len(VOCABULARY)}"
            )
            self.submit_button.setEnabled(False)
            self.input_box.setEnabled(False)
            QMessageBox.information(self, "LexiType", "Completed. You can restart.")

        self.stats_label.setText(
            f"Stats: Correct {self.correct_count} | Wrong {self.wrong_count}"
        )
        self.input_box.setFocus()

    def submit_answer(self) -> None:
        if self.current_index >= len(VOCABULARY):
            return

        typed_text = self.input_box.text().strip()
        correct_word, _ = self.current_item()

        if typed_text == correct_word:
            self.correct_count += 1
            self.status_label.setText("Correct")
        else:
            self.wrong_count += 1
            self.status_label.setText(f"Wrong: correct answer is {correct_word}")

        self.current_index += 1
        self.input_box.clear()
        self.update_view()

    def restart_session(self) -> None:
        self.correct_count = 0
        self.wrong_count = 0
        self.current_index = 0
        self.status_label.setText(" ")
        self.input_box.clear()
        self.input_box.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.update_view()


def main() -> int:
    app = QApplication(sys.argv)
    window = LexiTypeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
