# WinDbg

## Execution Control

| Command | Description                            |
| ------- | -------------------------------------- |
| `g`     | Continue execution                     |
| `p`     | Step over (next instruction)           |
| `t`     | Step into (follow call)                |
| `gu`    | Execute until current function returns |

## Breakpoints

| Command        | Description      |
| -------------- | ---------------- |
| `bp <address>` | Set breakpoint   |
| `bl`           | List breakpoints |

## Call Stack

| Command | Description                       |
| ------- | --------------------------------- |
| `k`     | Display call stack                |
| `kp`    | Display call stack with arguments |

## Useful One-liners

| Command        | Description                                              |
| -------------- | -------------------------------------------------------- |
| `bp @$exentry` | Set breakpoint at entry point                            |
| `bp @$scopeip` | Set breakpoint at current instruction pointer            |
| `!peb`         | Display PEB                                              |
| `dps @esp`     | Display stack contents with symbols (use `@rsp` for x64) |
| `db <address>` | Display raw memory bytes                                 |
