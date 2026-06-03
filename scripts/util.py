import socket

KENREL32_TO_BASE_THREAD_INIT_THUNK_OFFSET = 0x1FCB0
KERNEL32_TO_VIRTUAL_PROTECT_STUB_OFFSET = 0x20760


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

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
