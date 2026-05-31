from typing import Dict
from ...core.buffer import SocketBuffer


class BodyReader:
    """Read HTTP/1.1 body variants."""

    @classmethod
    def read(cls, buf: SocketBuffer, headers: Dict[str, str]) -> bytes:
        te = headers.get("Transfer-Encoding", "")
        if "chunked" in te.lower():
            return cls._read_chunked(buf)
        cl = headers.get("Content-Length")
        if cl is not None:
            return cls._read_fixed(buf, int(cl))
        # Read until close
        return cls._read_until_close(buf)

    @classmethod
    def _read_fixed(cls, buf: SocketBuffer, length: int) -> bytes:
        return buf.read(length)

    @classmethod
    def _read_chunked(cls, buf: SocketBuffer) -> bytes:
        body = bytearray()
        while True:
            line = buf.readline()
            size_str = line.split(b";")[0].strip()
            try:
                size = int(size_str, 16)
            except ValueError:
                break
            if size == 0:
                # Read trailing headers
                while True:
                    t = buf.readline()
                    if t in (b"\r\n", b"\n", b""):
                        break
                break
            chunk = buf.read(size)
            body.extend(chunk)
            buf.read(2)  # \r\n
        return bytes(body)

    @classmethod
    def _read_until_close(cls, buf: SocketBuffer) -> bytes:
        data = bytearray()
        while True:
            try:
                chunk = buf.read(4096)
                data.extend(chunk)
            except ConnectionError:
                break
        return bytes(data)
