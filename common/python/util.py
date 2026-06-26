import os
import socket
import struct
import subprocess


def find_exe(script_path: str, name: str) -> str:
    """Locate <name>.exe in the same directory as script_path."""
    return os.path.join(os.path.dirname(os.path.abspath(script_path)), f"{name}.exe")


def u32(x: int) -> int:
    return x & 0xFFFFFFFF


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
        self.sock: socket.socket | None = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, data: bytes):
        assert self.sock

        self.sock.sendall(data)

    def recvuntil(self, delimiter: bytes) -> bytes:
        assert self.sock

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


class Process:
    def __init__(self, cmd):
        self.cmd = cmd
        self.proc: subprocess.Popen[bytes] | None = None

    def connect(self):
        self.proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    def send(self, data: bytes):
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def recvuntil(self, delimiter: bytes) -> bytes:
        assert self.proc and self.proc.stdout
        buf = b""
        while not buf.endswith(delimiter):
            chunk = self.proc.stdout.read(1)
            if not chunk:
                raise ConnectionError("Process closed before delimiter was received")
            buf += chunk
        return buf

    def kill(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
