#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CMD_GET_CONTENT 1
#define CMD_SET_CONTENT 2
#define CMD_SET_NAME 3

char name[0x1000];

struct Content {
    char content[10];
    unsigned int len;
};

int func(void) {
    const HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    struct Content content = { 0 };
    DWORD br;
    unsigned int cmd = 0;
    name[0] = '\0';

    while (1) {
        if (name[0] != '\0') printf("Hello %s\n", name);
        printf("cmd: ");
        scanf_s("%d", &cmd);

        switch (cmd) {
        case CMD_GET_CONTENT:
            if (content.len == 0) {
                printf("Content is empty!\n");
                break;
            }

            for (unsigned int i = 0; i < content.len; i++) {
                printf("%02X ", (unsigned char)content.content[i]);
            }
            printf("\n");
            break;

        case CMD_SET_CONTENT:
            if (content.len == 0) {
                printf("content length: ");
                scanf_s("%d", &cmd);

                if (cmd > 0x10) {
                    printf("Invalid content length!\n");
                    break;
                }

                content.len = cmd;
            }

            printf("content: ");

            ReadFile(hStdin, content.content, content.len, &br, NULL);

            if (br >= 2)
                content.content[br - 2] = '\0';
            else
                content.content[0] = '\0';
            break;
        case CMD_SET_NAME:
            printf("name: ");
            ReadFile(hStdin, name, 0x1000, &br, NULL);

            if (br >= 2)
                name[br - 2] = '\0';
            else
                name[0] = '\0';
            break;
        default:
            goto END;
        }
    }
END:
    return 0;
}

int main(void) {
    int ret;
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    printf("Hello!\n");
    ret = func();
    printf("Bye!\n");
    return ret;
}
