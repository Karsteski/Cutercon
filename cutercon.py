#!/usr/bin/env python3
from enum import IntEnum
import socket
import select
import struct
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

    cuterconSocket = None

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
        """
        Create new socket w/ the address & protocol family (AF_INET is cute).
        SOCK_STREAM is a type of socket known as a stream socket,
        providing two-way communication between client and server.

        Call disconnect() after finishing with the socket!
        """
        self.cuterconSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cuterconSocket.connect((self.host, self.port))
        self._sendData(PacketType.Login, self.password)

    def disconnect(self):
        """
        Always close socket after finishing!
        """
        if self.cuterconSocket is not None:
            self.cuterconSocket.close()
            self.cuterconSocket = None

    def _readData(self, length):
        data = b""

        # Ensures all incoming bytes are read.
        while len(data) < length:
            data += self.cuterconSocket.recv(length - len(data))
        return data

    def _sendData(self, outgoingPacketType, outgoingPacketData):
        if self.cuterconSocket is None:
            raise CuterconException("A socket must be connected before sending data.")

        INITIAL_BYTE = 0
        EMPTY_TWO_BYTE_STRING = b"\x00\x00"

        # Must first send a request packet.
        outgoingPayload = (
            struct.pack("<ii", INITIAL_BYTE, outgoingPacketType)
            + outgoingPacketData.encode("utf8")
            + EMPTY_TWO_BYTE_STRING
        )

        outgoingPayloadLength = struct.pack("<i", len(outgoingPayload))
        self.cuterconSocket.send(outgoingPayloadLength + outgoingPayload)

        # Now read response packets.
        incomingData = ""  # Must be defined outside loop for concatenation

        while True:
            # First, read a packet
            BYTES_IN_32BIT_INT = 4
            BYTES_IN_ID_AND_TYPE_FIELD = 8

            # Note that unpack returns a tuple even for one item.
            # The empty items are "thrown" away.
            (incomingPayloadLength,) = struct.unpack("<i", self._readData(BYTES_IN_32BIT_INT))
            incomingPayload = self._readData(incomingPayloadLength)
            incomingPayloadID, incomingPayloadType = struct.unpack("<ii", incomingPayload[:BYTES_IN_ID_AND_TYPE_FIELD])
            incomingDataPartial, incomingPayloadPadding = (
                incomingPayload[BYTES_IN_ID_AND_TYPE_FIELD:-2],
                incomingPayload[-2:],
            )

            # Sanity checking
            if incomingPayloadPadding != b"\x00\x00":
                raise CuterconException("Incorrect packet padding!")

            WRONG_PASSWORD_ID = -1
            if incomingPayloadID == WRONG_PASSWORD_ID:
                raise CuterconException("Authentication failed: Wrong password!")

            # Store response
            incomingData += incomingDataPartial.decode("utf8")

            # Return response if no more data to receive
            TIMEOUT = 0.0  # A timeout value of zero specifies a poll and never blocks.
            if len(select.select([self.cuterconSocket], [], [], TIMEOUT)[0]) == 0:
                return incomingData

    def command(self, command):
        result = self._sendData(PacketType.Command, command)
        return result


class CuterconQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cutercon")
        self.setWindowIcon(QIcon("./minecraft-logo.ico"))
        self.resize(500, 500)  # width, height

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.outputField = QTextEdit()
        self.inputField = QLineEdit(returnPressed=self.sendCommand)
        # self.inputField = QLineEdit(returnPressed=self.mirrorText)

        layout.addWidget(self.outputField)
        layout.addWidget(self.inputField)

    def sendCommand(self):
        commandText = self.inputField.text()

        try:
            with Cutercon(HOST, PASSWORD, PORT) as rcon:
                print("# Connecting to %s:%i..." % (HOST, PORT))
                try:
                    rcon.command(commandText)
                except (ConnectionResetError, ConnectionAbortedError):
                    print("Server connection termined, perhaps it crashed or was stopped...")
        except ConnectionRefusedError:
            print("The server refused the connection!")
        except ConnectionError as error:
            print(error)

    def mirrorText(self):
        inputText = self.inputField.text()
        self.outputField.setText("Output: {0}".format(inputText))


if __name__ == "__main__":
    # Perhaps wrap below in Run() and Exit()
    app = QApplication([])

    window = CuterconQt()
    window.show()

    sys.exit(app.exec())
