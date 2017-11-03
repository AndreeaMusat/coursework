#include "list.h"
#include "hashtable.h"

/* Author: Andreea-Alexandra Musat, 333CA */

#define MAX_COMMAND_LEN 20000

static const char error_msg0[] = "[Error]: Wrong argument for resize command.";
static const char error_msg1[] = "[Error]: Wrong command";
static const char error_msg2[] = "[Error]: Input file not found";
static const char error_msg3[] = "[Error]: Wrong command line arguments.";

int is_number(char string[])
{
	int n = strlen(string);
	int i;

	for (i = 0; i < n; i++)
		if (string[i] < '0' || string[i] > '9')
			return 0;

	return 1;
}

int parseInput(FILE *fin, struct Hashtable **h)
{

	char line[MAX_COMMAND_LEN];
	char *token = NULL;
	char sep[] = "\n \0";

	while (fgets(line, MAX_COMMAND_LEN, fin) != NULL) {

		unsigned int cnt = 0;
		char array[3][MAX_COMMAND_LEN];

		memset(array, 0, sizeof(array[0][0]) * 3 * MAX_COMMAND_LEN);

		token = strtok(line, sep);
		while (token != NULL) {
			strcpy(array[cnt], token);
			cnt++;
			token = strtok(NULL, sep);
		}

		/* Check if the first word of the command is a known one. */
		/* If so, call the corresponding function. Otherwise, a */
		/* message error will be printed and at the end the program */
		/* will return -1. */
		if (strcmp(array[0], "add") == 0)
			if (strlen(array[1]) > 0)
				addWordHash(*h, array[1]);
			else
				return -1;

		else if (strcmp(array[0], "remove") == 0)
			if (strlen(array[1]) > 0)
				removeWordHash(*h, array[1]);
			else
				return -1;

		else if (strcmp(array[0], "find") == 0)
			if (strlen(array[1]) > 0)
				findWordHash(*h, array[1], array[2]);
			else
				return -1;

		else if (strcmp(array[0], "clear") == 0)
			clearHash(*h);

		else if (strcmp(array[0], "print_bucket") == 0)
			if (strlen(array[1]) > 0 && is_number(array[1]))
				printBucket(*h, array[1], array[2]);
			else
				return -1;

		else if (strcmp(array[0], "print") == 0)
			printHash(*h, array[1]);

		else if (strcmp(array[0], "resize") == 0) {

			if (strcmp(array[1], "double") == 0) {
				*h = doubleHash(h);
			} else if (strcmp(array[1], "halve") == 0) {
				*h = halveHash(h);
			} else {
				fprintf(stderr, "%s\n", error_msg0);
				return -1;
			}
		} else if (strlen(array[0]) > 0) {
			fprintf(stderr, "%s: \"%s\".\n", error_msg1, array[0]);
			return -1;
		}
	}
	return 1;
}

int main(int argc, char *argv[])
{
	unsigned int size, i;
	int res;
	struct Hashtable *h = calloc(1, sizeof(struct Hashtable));

	/* Check if the correct number of command line arguments was given */
	if (argc < 2) {
		fprintf(stderr, "%s\n", error_msg3);
		return -1;
	}

	/* Set the size of the hashtable and initialize it */
	size = atoi(argv[1]);
	initHash(size, &h);

	/* Parse the input files (if given) or the ones from stdin otherwise. */
	/* If any error is encountered, a negative value will be returned. */
	if (argc > 2) {
		for (i = 2; i < (unsigned int)argc; i++) {
			FILE *fin = fopen(argv[i], "r");

			if (fin == NULL) {
				fprintf(stderr, "%s\n", error_msg2);
				return -1;
			}

			res = parseInput(fin, &h);

			fclose(fin);

			if (res < 0)
				return -1;

		}
	} else {
		res = parseInput(stdin, &h);
		if (res < 0)
			return -1;
	}

	/* free the memory */
	for (i = 0; i < h->size; i++) {
		removeList(h->buckets[i]);
		free(h->buckets[i]);
	}

	if (h->buckets != NULL)
		free(h->buckets);

	if (h != NULL)
		free(h);

	return 0;
}
