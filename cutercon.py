import sys

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLineEdit, QTextEdit
from PyQt6.QtGui import QIcon

# Temp globals for testing...
HOST = "192.168.0.10"
PASSWORD = "password"
PORT = 25575


class CuterconQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cutercon")
        self.setWindowIcon(QIcon("./minecraft-logo.ico"))
        self.resize(500, 500)  # width, height

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.outputField = QTextEdit()
        self.inputField = QLineEdit(returnPressed=self.mirrorText)

        layout.addWidget(self.outputField)
        layout.addWidget(self.inputField)

    def mirrorText(self):
        inputText = self.inputField.text()
        self.outputField.setText("Output: {0}".format(inputText))


if __name__ == "__main__":
    # Perhaps wrap below in Run() and Exit()
    app = QApplication([])

    window = CuterconQt()
    window.show()

    sys.exit(app.exec())
