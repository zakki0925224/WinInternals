#include <stdio.h>

void func(const int argc, char** argv) {
	char data[512] = {0};

	FILE* fp;
	if (argc != 2) {
		printf("argc != 2\n");
		return;
	}

	fopen_s(&fp, argv[1], "rb");
	if (!fp) {
		printf("Failed to open %s!\n", argv[1]);
		return;
	}

#pragma warning(suppress: 6386)
	// buffer overflow
	fread(data, 1, 1024, fp);
}

int main(int argc, char** argv) {
	printf("start\n");
	func(argc, argv);
	printf("end\n");
	return 0;
}