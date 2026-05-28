#include <stdio.h>
#include <Windows.h>
#include <winternl.h>

int main(void) {
	PTEB teb = (PTEB)__readgsqword(offsetof(NT_TIB, Self));
	// PTEB teb = NtCurrentTeb();
	PPEB peb = teb->ProcessEnvironmentBlock;
	PLIST_ENTRY head = &peb->Ldr->InMemoryOrderModuleList;

	for (PLIST_ENTRY cur = head->Flink; cur != head; cur = cur->Flink) {
		PLDR_DATA_TABLE_ENTRY entry = CONTAINING_RECORD(cur, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);

		wprintf(L"Base: %p Name: %wZ\n", entry->DllBase, &entry->FullDllName);
	}

	return 0;
}