import socket
import threading
from typing import List, Tuple

from client import Client


class Server:

    def __init__(self, address: Tuple[str, int]) -> None:
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)
        self.clients: List[Client] = []
        self.running = False


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
                return


    def stop(self) -> None:
        if self.running:
            self.running = False
            print("Stopping server...")
            for client in self.clients:
                client.disconnect()
            self.socket.close()
    
    
    def get_newest_clip_holder(self) -> Client:
        newest = self.clients[0]
        for client in self.clients:
            if client.last_updated > newest.last_updated:
                newest = client
        return newest
    

    def update_clients(self, clip: str, owner: Client) -> None:
        for client in self.clients:
            if client != owner:
                client.update_clip(clip)


    def main_loop(self) -> None:
        try:
            while self.running:
                if len(self.clients) > 0:
                    newest_client = self.get_newest_clip_holder()
                    self.update_clients(newest_client.get_clip(), newest_client)
        
        except KeyboardInterrupt:
            self.stop()
            return


    def start(self) -> None:
        print(f"Starting server on {self.address[0]}:{self.address[1]}")
        self.running = True
        listener = threading.Thread(target=self.listen)
        listener.start()
        self.main_loop()
        print("Server stopped")

