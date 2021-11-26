import socket
import time
import pyperclip
from typing import Tuple


class Client:

    def __init__(self, sock: socket.socket, address: Tuple[str, int]) -> None:
        self.socket = sock
        self.address = address
        self.last_updated = time.time_ns()
    

    def disconnect(self) -> None:
        self.socket.close()


    def update_clip(self, clip: str) -> None:
        pyperclip.copy(clip)

    
    def get_clip(self) -> str:
        return pyperclip.paste()

