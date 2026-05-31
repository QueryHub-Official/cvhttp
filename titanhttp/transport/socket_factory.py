import socket
from typing import Tuple
from ..types import URLComponents


class SocketFactory:
    @staticmethod
    def create_tcp_socket(family: int = socket.AF_INET) -> socket.socket:
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock

    @staticmethod
    def connect(sock: socket.socket, addr: Tuple, timeout: float = 30):
        sock.settimeout(timeout)
        sock.connect(addr)
