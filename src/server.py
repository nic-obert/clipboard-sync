import socket
import threading
from typing import List, Tuple

from client import Client


class Server:

    def __init__(self, address: Tuple[str, int]) -> None:
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.clients: List[Client] = []
        self.running = False
        self.current_clip: str = ''


    def listen(self) -> None:
        try:
            self.socket.listen()
            while self.running:
                client_socket, client_address = self.socket.accept()
                print(f"Client connected from {client_address[0]}:{client_address[1]}")
                client = Client(client_socket, client_address)
                self.clients.append(client)
        
        except KeyboardInterrupt:
                self.stop()


    def stop(self) -> None:
        if self.running:
            self.running = False
            print("Stopping server...")
            for client in self.clients:
                client.disconnect()
            self.socket.close()
        print("Server stopped")
    

    def update_clipboard(self, clip: str, owner: Client) -> None:
        for client in self.clients:
            if client != owner:
                try:
                    client.send_clip(clip)
                except BrokenPipeError:
                    client.disconnect()
                    self.clients.remove(client)


    def get_updates(self) -> Client:
        newest_clip_holder = self.clients[0]
        for client in self.clients:
            client.update()
            if client.last_updated > newest_clip_holder.last_updated:
                newest_clip_holder = client

        return newest_clip_holder


    def main_loop(self) -> None:
        try:
            while self.running:
                if len(self.clients) > 0:
                    newest_clip_holder = self.get_updates()
                    if newest_clip_holder.clip != self.current_clip:
                        self.current_clip = newest_clip_holder.clip
                        self.update_clipboard(self.current_clip, newest_clip_holder)

        except KeyboardInterrupt:
            self.stop()


    def start(self) -> None:
        print(f"Starting server on {self.address[0]}:{self.address[1]}")
        self.running = True
        listener = threading.Thread(target=self.listen)
        listener.start()
        self.main_loop()

