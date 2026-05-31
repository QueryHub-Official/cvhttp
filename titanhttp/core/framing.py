import struct
from typing import Tuple
from dataclasses import dataclass


@dataclass
class HTTP2Frame:
    """HTTP/2 frame structure per RFC 7540."""

    length: int
    type: int
    flags: int
    stream_id: int
    payload: bytes

    FRAME_HEADER_SIZE = 9

    @classmethod
    def parse_header(cls, data: bytes) -> Tuple[int, int, int, int]:
        if len(data) < 9:
            raise ValueError("Need 9 bytes for frame header")
        length = (data[0] << 16) | (data[1] << 8) | data[2]
        ftype = data[3]
        flags = data[4]
        stream_id = struct.unpack(">I", data[5:9])[0] & 0x7FFFFFFF
        return length, ftype, flags, stream_id

    @classmethod
    def from_bytes(cls, header: bytes, payload: bytes) -> "HTTP2Frame":
        length, ftype, flags, stream_id = cls.parse_header(header)
        return cls(length, ftype, flags, stream_id, payload)

    def to_bytes(self) -> bytes:
        header = struct.pack(
            ">I", self.length
        )[1:]  # 24-bit length
        header += struct.pack(">BBI", self.type, self.flags, self.stream_id & 0x7FFFFFFF)
        return header + self.payload

    def __repr__(self) -> str:
        return f"HTTP2Frame(type={self.type}, flags={self.flags}, stream={self.stream_id}, len={self.length})"
