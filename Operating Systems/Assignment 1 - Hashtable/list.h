/* Author: Andreea-Alexandra Musat, 333CA */

#pragma once
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#define MAXLEN 20000

struct Node {
	char word[MAXLEN];
	struct Node *next;
	struct Node *prev;
};

struct LinkedList {
	struct Node *head;
	struct Node *tail;
};

/* Add node at the end of the list */
void append(struct LinkedList *list, char word[]);

/* Remove node with given value - it may not exist */
void removeWord(struct LinkedList *list, char word[]);

/* Return 1 if word exists and 0 otherwise */
int findWord(struct LinkedList *list, char word[]);

/* Print the list on a single line */
void printList(struct LinkedList *list, FILE *fout);

/* delete the list */
void removeList(struct LinkedList *list);
