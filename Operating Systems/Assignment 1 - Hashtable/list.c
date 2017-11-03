/* Author: Andreea-Alexandra Musat, 333CA */

#include "list.h"

void append(struct LinkedList *list, char word[])
{
	/* Create a new pointer to a node */
	struct Node *new_node = calloc(1, sizeof(struct Node));

	if (list == NULL)
		return;

	/* Set the key and previous and next nodes */
	strcpy(new_node->word, word);
	new_node->next = NULL;
	new_node->prev = NULL;

	/* If the list is empty, set the head and the tail */
	if (list->head == NULL && list->tail == NULL) {
		list->head = new_node;
		list->tail = new_node;
	} else {
		/* Otherwise add the node at the end and just set the tail */
		list->tail->next = new_node;
		new_node->prev = list->tail;
		list->tail = new_node;
	}
}

void removeWord(struct LinkedList *list, char word[])
{
	struct Node *current = list->head;

	if (list == NULL)
		return;

	/* Check every node in the list until the one with the */
	/*	given key is found. Set its previous and/or next   */
	/*	nodes pointers so that it is removed and then free */
	/*	the memory.                                        */
	while (current != NULL) {
		if (strcmp(current->word, word) == 0) {
			if (current == list->head)
				list->head = list->head->next;
			if (current == list->tail)
				list->tail = list->tail->prev;

			if (current->prev != NULL)
				current->prev->next = current->next;
			if (current->next != NULL)
				current->next->prev = current->prev;

			free(current);

			break;
		}
		current = current->next;
	}
}

int findWord(struct LinkedList *list, char word[])
{
	struct Node *current = list->head;

	while (current != NULL) {
		if (strcmp(current->word, word) == 0)
			return 1;
		current = current->next;
	}
	return 0;
}

void printList(struct LinkedList *list, FILE *fout)
{
	int cnt = 0;
	struct Node *current = list->head;

	if (list == NULL)
		return;

	/* As long as the current node is not null, just print it. */
	while (current != NULL) {
		fprintf(fout, "%s ", current->word);
		current = current->next;

		cnt++;
	}

	if (list->head != NULL)
		fprintf(fout, "\n");
}

void removeList(struct LinkedList *list)
{
	struct Node *tmp;

	if (list == NULL)
		return;

	/* Free every node from the list */
	while (list->head != NULL) {
		tmp = list->head;
		list->head = list->head->next;
		free(tmp);
	}

	/* Set the head and tail to null */
	list->head = NULL;
	list->tail = NULL;
}
