#include <stdio.h>
#include <Windows.h>

#define INSN_BYE 0x00
#define INSN_READ 0x31
#define INSN_WRITE 0x32
#define INSN_ADD 0x33

#define N 0x100

BYTE* memory;

size_t regA;
size_t regB;
size_t regC;

BOOL Check(size_t offset)
{
    return offset < N && offset + sizeof(size_t) <= N;
}

_declspec(noinline)
void CopyToRegA(void* data)
{
    regA = *(size_t*)data;
}

_declspec(noinline)
void CopyToRegB(void* data)
{
    regB = *(size_t*)data;
}
_declspec(noinline)
void CopyToRegC(void* data)
{
    regC = *(size_t*)data;
}

_declspec(noinline)
void CopyFromRegA(void* data)
{
    *(size_t*)data = regA;
}

_declspec(noinline)
void CopyFromRegB(void* data)
{
    *(size_t*)data = regB;
}

_declspec(noinline)
void CopyFromRegC(void* data)
{
    *(size_t*)data = regC;
}

_declspec(noinline)
void AddA(size_t value)
{
    regA += value;
}

_declspec(noinline)
void AddB(size_t value)
{
    regB += value;
}

_declspec(noinline)
void AddC(size_t value)
{
    regC += value;
}

_declspec(noinline)
void ReadMem(size_t reg, size_t offset)
{
    void (*func)(void*);

    if (!Check(offset)) return;

    switch (reg)
    {
    case 0:
        func = CopyToRegA;
        break;
    case 1:
        func = CopyToRegB;
        break;
    case 2:
        func = CopyToRegC;
        break;
    }

    void* ptr = memory + offset;

    func(ptr);
}

_declspec(noinline)
void WriteMem(size_t reg, size_t offset)
{
    void (*func)(void*);

    if (!Check(offset)) return;

    switch (reg)
    {
    case 0:
        func = CopyFromRegA;
        break;
    case 1:
        func = CopyFromRegB;
        break;
    case 2:
        func = CopyFromRegC;
        break;
    }

    void* ptr = memory + offset;

    func(ptr);
}

_declspec(noinline)
void Add(size_t reg, size_t value)
{
    void (*func)(void*);

    switch (reg)
    {
    case 0:
        func = AddA;
        break;
    case 1:
        func = AddB;
        break;
    case 2:
        func = AddC;
        break;
    }

    func(value);
}

int main(int argc, char** argv)
{
    FILE* fp;
    if (argc != 2)
    {
        printf("argc != 2\n");
        return 1;
    }
    fopen_s(&fp, argv[1], "rb");
    if (!fp)
    {
        printf("Failed to open %s!\n", argv[1]);
        return 2;
    }

    BYTE localMem[N];

    memory = localMem;
    fread(memory, 1, N, fp);
    fclose(fp);

    BYTE op;
    size_t reg, offset, value;

#define CHECKED_FETCH(ty, val, it) do { \
        if ((it) + sizeof(ty) >= memory + N) return 5; \
        (val) = *(ty*)(it); (it) += sizeof(ty); \
    } while(0)

    BYTE* it = memory;

    while (it < memory + N)
    {
        op = *it++;

        switch (op)
        {
        case INSN_READ:
            CHECKED_FETCH(size_t, reg, it);
            CHECKED_FETCH(size_t, offset, it);
            ReadMem(reg, offset);
            break;
        case INSN_WRITE:
            CHECKED_FETCH(size_t, reg, it);
            CHECKED_FETCH(size_t, offset, it);
            WriteMem(reg, offset);
            break;
        case INSN_ADD:
            CHECKED_FETCH(size_t, reg, it);
            CHECKED_FETCH(size_t, value, it);
            Add(reg, value);
            break;
        case INSN_BYE:
            printf("Bye!\n");
            return 0;
        default:
            return 3;
        }
    }

    printf("Finish!\n");
    return 0;
}
