#define _CRT_RAND_S
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define CMD_ENTR_HIDDEN_MODE 1
#define CMD_READ_CONTENT 2
#define CMD_WRITE_CONTENT 3

int main(void)
{
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	unsigned int hiddenCode;
	char content[32] = { 0 };
	unsigned int contentLen = 0;
	unsigned int cmd = 0;

	if (rand_s(&hiddenCode) == EINVAL) {
		printf("Failed to rand_s\n");
		return 1;
	}

	while (1)
	{
		printf("cmd: ");
		scanf_s("%d", &cmd);

		switch (cmd)
		{
		case CMD_ENTR_HIDDEN_MODE:
			printf("hidden code: ");
			scanf_s("%d", &cmd);

			if (cmd == hiddenCode) {
				printf("Welcome to hidden mode!\n");
			}
			else {
				printf("Wrong!\n");
			}

			break;

		case CMD_READ_CONTENT:
			if (contentLen == 0) {
				printf("Content is empty!\n");
				break;
			}

			for (unsigned int i = 0; i < contentLen; i++) {
				printf("%02x ", (unsigned char)content[i]);
			}

			printf("\n");
			break;

		case CMD_WRITE_CONTENT:
			printf("content length: ");
			scanf_s("%d", &contentLen);

			if (contentLen > 32) {
				printf("Invalid content length!\n");
				break;
			}

			printf("content: ");
			scanf_s("%s", content, contentLen);
			break;

		default:
			goto END;
		}
	}
END:
	printf("Bye!\n");
	return 0;
}
