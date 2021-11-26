import socket

from server import Server


def get_address() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main() -> None:
    address = get_address()
    port = 50018

    server = Server((address, port))
    server.start()


if __name__ == "__main__":
    main()

