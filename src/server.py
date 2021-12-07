import socket
import threading
import time
import os
from typing import List, Tuple, final

from client import Client


class Server:

    SCAN_DELAY = 0.1

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
            self.socket.listen(5)
            while self.running:
                client_socket, client_address = self.socket.accept()
                print(f"Client connected from {client_address[0]}:{client_address[1]}")
                
                client = Client(client_socket, client_address)
                self.clients.append(client)
                print(f"Clients currently connected: {len(self.clients)}")

                client_thread = threading.Thread(target=self.client_thread, args=(client,))
                client_thread.start()
        
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        
        except Exception as e:
            print(e)

        finally:
            self.stop()


    def remove_client(self, client: Client) -> None:
        if client.connected:
            client.disconnect()
            print(f"Removing client from {client.address[0]}:{client.address[1]}")
        
        try:
            self.clients.remove(client)
            print(f"Client {client.address[0]}:{client.address[1]} removed")
        except ValueError:
            pass


    def client_thread(self, client: Client) -> None:
        try:
            while self.running and client.connected:
                client.update()
                time.sleep(self.SCAN_DELAY)

        except KeyboardInterrupt:
            self.stop()
        
        except Exception as e:
            print(e)

        self.remove_client(client)


    def stop(self) -> None:
        if self.running:
            self.running = False
            print("Stopping server...")
            
            for client in self.clients:
                self.remove_client(client)
            
            self.socket.close()
            print("Server stopped")
            os._exit(0)
    

    def update_clipboard(self, clip: str, owner: Client) -> None:
        for client in self.clients:
            if client != owner:
                try:
                    client.send_clip(clip)
                
                except BrokenPipeError:
                    self.remove_client(client)


    def get_updates(self) -> Client:
        newest_clip_holder = self.clients[0]

        for client in self.clients:
            if not client.update_connection_status():
                self.remove_client(client)
                continue

            if client.last_updated > newest_clip_holder.last_updated:
                newest_clip_holder = client
            
        return newest_clip_holder


    def main_loop(self) -> None:
        try:
            while self.running:
                if len(self.clients) == 0:
                    continue

                newest_clip_holder = self.get_updates()
                if newest_clip_holder.clip != self.current_clip:
                    self.current_clip = newest_clip_holder.clip
                    #print(f"New clipboard: {self.current_clip}")
                    self.update_clipboard(self.current_clip, newest_clip_holder)
                
                time.sleep(self.SCAN_DELAY)

        except KeyboardInterrupt:
            self.stop()


    def start(self) -> None:
        print(f"Starting server on {self.address[0]}:{self.address[1]}")
        self.running = True
        listener = threading.Thread(target=self.listen)
        listener.start()
        self.main_loop()

