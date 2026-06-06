import socket
import struct


def le32(x: int) -> bytes:
    return struct.pack("<I", x)


def le64(x: int) -> bytes:
    return struct.pack("<Q", x)


def to_u32(data: bytes, pos: int) -> int:
    return struct.unpack("<I", data[pos : pos + 4])[0]


def to_u64(data: bytes, pos: int) -> int:
    return struct.unpack("<Q", data[pos : pos + 8])[0]


class Socket:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = int(port)
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, data: bytes):
        self.sock.sendall(data)

    def recvuntil(self, delimiter: bytes) -> bytes:
        buf = b""
        while not buf.endswith(delimiter):
            chunk = self.sock.recv(1)
            if not chunk:
                raise ConnectionError("Connection closed before delimiter was received")
            buf += chunk
        return buf

    def kill(self):
        if self.sock:
            self.sock.close()
            self.sock = None
