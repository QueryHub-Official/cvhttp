import socket
import struct
from typing import Optional


class SOCKS5:
    @staticmethod
    def connect(
        proxy_host: str,
        proxy_port: int,
        target_host: str,
        target_port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((proxy_host, proxy_port))

        # Greeting
        auth = [0x00] if not username else [0x00, 0x02]
        sock.sendall(bytes([0x05, len(auth)] + auth))
        resp = sock.recv(2)
        if resp[0] != 0x05:
            raise ConnectionError("SOCKS5 version mismatch")

        if resp[1] == 0x02 and username:
            auth_data = bytes([0x01, len(username)]) + username.encode()
            auth_data += bytes([len(password or "")]) + (password or "").encode()
            sock.sendall(auth_data)
            aresp = sock.recv(2)
            if aresp[1] != 0x00:
                raise ConnectionError("SOCKS5 auth failed")

        # Request
        req = bytes([0x05, 0x01, 0x00, 0x03])
        host_b = target_host.encode()
        req += bytes([len(host_b)]) + host_b
        req += struct.pack(">H", target_port)
        sock.sendall(req)
        resp = sock.recv(10)
        if resp[1] != 0x00:
            raise ConnectionError(f"SOCKS5 connect failed: {resp[1]}")
        return sock
