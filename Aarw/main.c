#define _CRT_RAND_S
#include <stdio.h>
#include <stdlib.h>

#define CMD_ENTER_HIDDEN_MODE 1
#define CMD_REGISTER_FAV_NUMBER 2
#define CMD_SHOW_FAV_NUMBER 3

int hiddenCode = 0;
char isPro = 0;

int main(void)
{
	int cmd = 0;
	int favorites[10] = { 0 };
	int numOfFavorites = 0;
	int pos = 0;

	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	rand_s((unsigned int*)&hiddenCode);
	printf("===================================================\n");
	printf("FNR: Favorite Number Registry\n");
	printf("You can register up to 10 of your favorite numbers!\n");
	printf("===================================================\n");

	while (1)
	{
		if (isPro)
		{
			printf("****** Professional mode ******\n");
		}

		printf("cmd: ");
		scanf_s("%d", &cmd);

		switch (cmd)
		{
		case CMD_ENTER_HIDDEN_MODE:
			printf("hidden code: ");
			scanf_s("%d", &cmd);

			if (hiddenCode == cmd)
			{
				printf("Welcome to hidden mode!\n");
			}
			else {
				printf("Wrong!\n");
			}

			break;

		case CMD_REGISTER_FAV_NUMBER:
			if (numOfFavorites >= 10)
			{
				printf("You've already registered 10 favorite numbers!\n");
				printf("You need to overwrite any of the favorite numbers...\n");
				printf("What number do you want to overwrite? (You can choose 1 to 10) ");
				scanf_s("%d", &pos);
				pos--;
			}
			else {
				pos = numOfFavorites;
			}

			printf("Input your favorite value: ");
			scanf_s("%d", &cmd);
			favorites[pos] = cmd;
			numOfFavorites++;

			if (numOfFavorites >= 10) numOfFavorites = 10;
			printf("registered!\n");
			break;

		case CMD_SHOW_FAV_NUMBER:
			printf("What number do you want to read? (You can choose 1 to 10) ");
			scanf_s("%d", &pos);
			pos--;
			printf("number %d is %d\n", pos, favorites[pos]);
			break;

		default:
			goto END;
		}
	}

END:
printf("bye!\n");
return 0;
}
