# Windows calling conventions

## x86

### cdecl (Default)

```c
// Return value is stored in EAX, or EDX:EAX if the return value is larger than 32 bits.
int eax_or_edx = __cdecl func(int stack_arg1, int stack_arg2, ...)
```

### stdcall (Win32 API)

```c
int eax_or_edx = __stdcall func(int stack_arg1, int stack_arg2, ...)
```

### fastcall

```c
int eax_or_edx = __fastcall func(int ecx, int edx, int stack_arg1, int stack_arg2, ...)
```

## x64 (Normal integer arguments)

```c
__int64 rax = func(int rcx, int rdx, int r8, int r9, int stack_arg1, int stack_arg2, ...)
```
