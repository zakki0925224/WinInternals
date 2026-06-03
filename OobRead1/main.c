#include <stdio.h>
#include <Windows.h>

int main(void)
{
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	int input;
	int data[10];

	// set data
	data[0] = data[1] = 1;
	for (int i = 2; i < 10; i++) {
		data[i] = data[i - 1] + data[i - 2];
	}

	printf("Input (1~10): ");
	scanf_s("%d", &input);

	for (int i = 0; i < input; i++) {
		printf("%d\n", data[i]);
	}

	Sleep(100);
	return 0;
}