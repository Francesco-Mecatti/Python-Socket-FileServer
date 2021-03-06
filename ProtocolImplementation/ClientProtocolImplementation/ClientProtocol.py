import os
from ProtocolImplementation.Protocol import DIMBYTESNUM, BUFFSIZENUM, CODEBYTES, StatusHandler, ReliableTransmission
import socket
from typing import BinaryIO


class ProtocolHandler:
    def __init__(self, s: socket.socket):
        self.s: socket.socket = s
        self.status_handler = StatusHandler(self.s)

    def input(self):
        try:
            text = ReliableTransmission.recvstring(self.s)
            self.status_handler.ok()
            self.status_handler.response()
            input_text = input(text)
            input_text += "\n"
            self.s.sendall(input().encode())
            if not self.status_handler.is_code("OK", self.s.recv(CODEBYTES)):
                raise ConnectionError("Server not confirming")
            if not self.status_handler.is_code("End", self.s.recv(CODEBYTES)):
                raise ConnectionError("Server not ending")
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print("Error with transmission. Try again")

    def output(self):
        text = self.s.recv(BUFFSIZENUM).decode()
        self.status_handler.ok()
        if not self.status_handler.is_code("End", self.s.recv(CODEBYTES)):
            raise ConnectionError("Server not ending")
        else:
            print(text)

    def download_file(self, file):
        self.status_handler.ok()
        dim = int.from_bytes(self.s.recv(DIMBYTESNUM), 'big')
        received = 0
        while received < dim:
            data = self.s.recv(dim - received)
            file.write(data)
            received += len(data)
        if file.tell() != dim:
            self.status_handler.error_file_recv_incomplete()
            raise ConnectionError("FileRecvIncomplete")
        else:
            self.status_handler.ok()
        self.status_handler.end()

    def upload_file(self, file: BinaryIO, size: int):  # size [bytes]
        try:
            # print(size)
            size_b = size.to_bytes(DIMBYTESNUM, 'big')
        except OverflowError:
            self.status_handler.error_file_too_large()
            print("The selected file is too big")
        else:
            try:
                self.status_handler.ok()
                self.s.sendall(size_b)
                self.s.sendall(file.read())
                data = self.s.recv(CODEBYTES)
                if self.status_handler.is_code("FileRecvIncomplete", data):
                    raise ConnectionError("Connection error, file incomplete")
                elif not self.status_handler.is_code("OK", data):
                    raise ConnectionError("Server not confirming")
                if not self.status_handler.is_code("End", self.s.recv(CODEBYTES)):
                    raise ConnectionError("Server not ending")
            except:
                print("Connection error. Try again")
                raise ConnectionError()


class FileHandler:
    def __init__(self, s: socket.socket):
        self.s: socket.socket = s
        self.protocol_handler = ProtocolHandler(self.s)
        self.status_handler = StatusHandler(self.s)

    def upload(self):
        filename = self.s.recv(BUFFSIZENUM).decode()
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                try:
                    self.protocol_handler.upload_file(file, os.path.getsize(filename))
                except:
                    print("Error")
                else:
                    print(f"File sent: {filename}")
        else:
            self.status_handler.error_file_not_found()
            print("File doesn't exist")

    def download(self):
        data = self.s.recv(CODEBYTES)
        if self.status_handler.is_code("FileNotFound", data):
            print("File not found")
            return
        if not self.status_handler.is_code("OK", data):
            raise ConnectionError("Server not confirming")
        filename = self.s.recv(BUFFSIZENUM).decode()
        with open(filename, 'wb') as file:
            try:
                self.protocol_handler.download_file(file)
            except:
                print("Error")
            else:
                print(f"File received: {filename}")
