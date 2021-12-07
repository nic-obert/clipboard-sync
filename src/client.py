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
        if self.connected:
            self.connected = False
            self.socket.close()
            print(f'Disconnected from {self.address}')

    
    def update_connection_status(self) -> bool:
        try:
            self.socket.send(b'p')
            return True
        except:
            self.disconnect()
            return False


    def send_clip(self, clip: str) -> None:
        self.socket.send(clip.encode('utf-8'))
    

    def update(self) -> None:
        try:
            clip = recvall(self.socket)
            if clip:
                self.clip = clip.decode('utf-8')
                self.last_updated = time.time_ns()
        
        except ConnectionResetError:
            self.disconnect()
        
        except Exception as e:
            print(e)
            self.disconnect()
        

    def __str__(self) -> str:
        return f'<Client: {self.address}>'
    

    def __repr__(self) -> str:
        return self.__str__()

