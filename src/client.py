import socket
import time
from typing import Tuple


def recvall(sock: socket.socket) -> bytes:
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


class Client:

    def __init__(self, sock: socket.socket, address: Tuple[str, int]) -> None:
        self.socket = sock
        self.address = address
        self.last_updated = time.time_ns()
        self.clip: str = ''
        self.connected = True
    

    def disconnect(self) -> None:
        self.socket.close()
        self.connected = False


    def send_clip(self, clip: str) -> None:
        self.socket.send(clip.encode('utf-8'))
    

    def update(self) -> None:
        clip = recvall(self.socket)
        if clip:
            self.clip = clip.decode('utf-8')
            self.last_updated = time.time_ns()

