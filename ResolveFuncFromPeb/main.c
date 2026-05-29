#include <stdio.h>
#include <Windows.h>
#include <winternl.h>
#include <assert.h>

static DWORD ror13HashA(const char* str) {
	DWORD hash = 0;

	while (*str) {
		hash = (hash >> 13) | (hash << (32 - 13));
		hash += (DWORD)*str++;
	}

	return hash;
}

static DWORD ror13HashW(const wchar_t* str) {
	DWORD hash = 0;

	while (*str) {
		hash = (hash >> 13) | (hash << (32 - 13));
		hash += (DWORD)*str++;
	}

	return hash;
}

static UNICODE_STRING getBaseDllName(const PLDR_DATA_TABLE_ENTRY entry) {
	return *(UNICODE_STRING *)entry->Reserved4;
}

static PVOID getDllBaseByName(const wchar_t* name) {
	const PTEB teb = NtCurrentTeb();
	const PPEB peb = teb->ProcessEnvironmentBlock;
	
	const PLIST_ENTRY head = &peb->Ldr->InMemoryOrderModuleList;
	PLIST_ENTRY cur = head->Flink;

	while (cur != head) {
		const PLDR_DATA_TABLE_ENTRY entry = CONTAINING_RECORD(cur, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
		const UNICODE_STRING baseDllName = getBaseDllName(entry);

		if (wcscmp(baseDllName.Buffer, name) == 0) {
			return entry->DllBase;
		}
		cur = cur->Flink;
	}

	return NULL;
}

static PVOID getDllBaseByHash(const DWORD hash) {
	const PTEB teb = NtCurrentTeb();
	const PPEB peb = teb->ProcessEnvironmentBlock;

	const PLIST_ENTRY head = &peb->Ldr->InMemoryOrderModuleList;
	PLIST_ENTRY cur = head->Flink;

	while (cur != head) {
		const PLDR_DATA_TABLE_ENTRY entry = CONTAINING_RECORD(cur, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
		const UNICODE_STRING baseDllName = getBaseDllName(entry);
		const DWORD dllNameHash = ror13HashW(baseDllName.Buffer);

		if (dllNameHash == hash) {
			return entry->DllBase;
		}
		cur = cur->Flink;
	}

	return NULL;
}

static PVOID getFunctionByName(const PVOID dllBase, const char* functionName) {
	const IMAGE_DOS_HEADER* dllDosHeader = dllBase;
	const IMAGE_NT_HEADERS* ntHeader = (IMAGE_NT_HEADERS*)((char*)dllBase + dllDosHeader->e_lfanew);
	
	const DWORD expRVA = ntHeader->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;

	if (!expRVA) {
		return NULL;
	}

	const IMAGE_EXPORT_DIRECTORY* exp = (IMAGE_EXPORT_DIRECTORY*)((char*)dllBase + expRVA);

	const DWORD* nameRVAs = (DWORD*)((char*)dllBase + exp->AddressOfNames);
	const DWORD* funcRVAs = (DWORD*)((char*)dllBase + exp->AddressOfFunctions);
	const WORD* nameOrdinals = (WORD*)((char*)dllBase + exp->AddressOfNameOrdinals);

	for (DWORD i = 0; i < exp->NumberOfNames; i++) {
		const char* name = (const char*)((char*)dllBase + nameRVAs[i]);

		if (strcmp(name, functionName) == 0) {
			WORD ord = nameOrdinals[i];
			return (PVOID)((char*)dllBase + funcRVAs[ord]);
		}
	}

	return NULL;
}

static PVOID getFunctionByHash(const PVOID dllBase, const DWORD hash) {
	const IMAGE_DOS_HEADER* dllDosHeader = dllBase;
	const IMAGE_NT_HEADERS* ntHeader = (IMAGE_NT_HEADERS*)((char*)dllBase + dllDosHeader->e_lfanew);

	const DWORD expRVA = ntHeader->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;

	if (!expRVA) {
		return NULL;
	}

	const IMAGE_EXPORT_DIRECTORY* exp = (IMAGE_EXPORT_DIRECTORY*)((char*)dllBase + expRVA);

	const DWORD* nameRVAs = (DWORD*)((char*)dllBase + exp->AddressOfNames);
	const DWORD* funcRVAs = (DWORD*)((char*)dllBase + exp->AddressOfFunctions);
	const WORD* nameOrdinals = (WORD*)((char*)dllBase + exp->AddressOfNameOrdinals);

	for (DWORD i = 0; i < exp->NumberOfNames; i++) {
		const char* name = (const char*)((char*)dllBase + nameRVAs[i]);
		const DWORD nameHash = ror13HashA(name);

		if (nameHash == hash) {
			WORD ord = nameOrdinals[i];
			return (PVOID)((char*)dllBase + funcRVAs[ord]);
		}
	}

	return NULL;
}

int main(void) {
	// by name
	const PVOID kernel32DllBase = getDllBaseByName(L"KERNEL32.DLL");
	const PVOID winExec = getFunctionByName(kernel32DllBase, "WinExec");

	wprintf(L"KERNEL32.DLL base: 0x%p\n", kernel32DllBase);
	wprintf(L"WinExec address: 0x%p\n", winExec);

	// by hash
	const DWORD kernel32Hash = ror13HashW(L"KERNEL32.DLL");
	const DWORD winExecHash = ror13HashA("WinExec");

	const PVOID kernel32DllBaseByHash = getDllBaseByHash(kernel32Hash);
	const PVOID winExecByHash = getFunctionByHash(kernel32DllBase, winExecHash);

	wprintf(L"KERNEL32.DLL base: 0x%p\n", kernel32DllBaseByHash);
	wprintf(L"WinExec address: 0x%p\n", winExecByHash);

	assert(kernel32DllBase == kernel32DllBaseByHash);
	assert(winExec == winExecByHash);

	return 0;
}