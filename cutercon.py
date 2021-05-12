from enum import IntEnum
import socket
import sys

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLineEdit, QTextEdit
from PyQt6.QtGui import QIcon

# Temp globals for testing...
HOST = "192.168.0.10"
PASSWORD = "password"
PORT = 25575


class PacketType(IntEnum):
    """
    Packet type field is a 32-bit little endian integer,
    indicating the purpose of the packet.
    """
    # Incoming payload is the output of the command. Commands can return nothing.
    CommandResponse = 0

    # Outgoing payload is command to be run, e.g. "time set 0".
    Command = 2

    # Outgoing payload is the RCON password set by the server.
    # Server returns packet w/ the same request ID upon success.
    # The return packet will be type 2 (Command)
    # A response with a request ID of -1 indicates a wrong password.
    Login = 3


class CuterconException(Exception):
    pass


class Cutercon(object):
    """
    Remote Console Client for Minecraft: Java Edition
    """

    cutercon_socket = None

    def __init__(self, host, password, port=25575):
        self.host = host
        self.password = password
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    # Guarantees socket is closed upon program exit.
    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        self.disconnect()

    def connect(self):
        # Create new socket w/ the address & protocol family (AF_INET is IPv4).
        # SOCK_STREAM is a type of socket known as a stream socket,
        # providing two-way communication between client and server.
        self.cutercon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self._sendData(PacketType.Login, self.password)

    def disconnect(self):
        if self.cutercon_socket is not None:
            self.socket.close()
            self.cutercon_socket = None

    def _readData(self, length):
        data = b""

        # Ensures all incoming bytes are read.
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data

    def _sendData(self, outputType, outputData):

    def command(self, command):


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
