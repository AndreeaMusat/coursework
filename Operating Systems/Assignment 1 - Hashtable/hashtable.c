/* Author: Andreea-Alexandra Musat, 333CA */

#include "list.h"
#include "hash.h"
#include "hashtable.h"

void initHash(unsigned int size, struct Hashtable **h)
{
	unsigned int i;

	(*h)->buckets = calloc(size, sizeof(struct LinkedList *));

	/* Allocate the lists and set the head and the tail to null */
	for (i = 0; i < size; i++) {
		(*h)->buckets[i] = calloc(1, sizeof(struct LinkedList));
		(*h)->buckets[i]->head = NULL;
		(*h)->buckets[i]->tail = NULL;
	}
	(*h)->size = size;

}

void addWordHash(struct Hashtable *h, char word[])
{
	unsigned int bucket_id = hash(word, h->size);

	/* Check if the word is already in its corresponding */
	/* bucket. If not, add it. */
	if (findWord(h->buckets[bucket_id], word) == 0)
		append(h->buckets[bucket_id], word);
}

void removeWordHash(struct Hashtable *h, char word[])
{
	unsigned int bucket_id = hash(word, h->size);

	/* Check if the word exists in the bucket and if so, */
	/* remove it. */
	if (findWord(h->buckets[bucket_id], word) != 0)
		removeWord(h->buckets[bucket_id], word);
}

void findWordHash(struct Hashtable *h, char word[], char option[])
{
	unsigned int found = 0;
	unsigned int bucket_id = hash(word, h->size);
	FILE *fout;

	/* Get the result of the find query */
	if (findWord(h->buckets[bucket_id], word) == 1)
		found = 1;

	/* Write the result to stdout (if a file name was not provided, */
	/* otherwise to the specific file). */
	if (strlen(option) == 0)
		fprintf(stdout, "%s\n", (found == 1) ? "True" : "False");
	else  {
		fout = fopen(option, "a");

		fprintf(fout, "%s\n", (found == 1) ? "True" : "False");
		fclose(fout);
	}
}

void clearHash(struct Hashtable *h)
{
	unsigned int i;

	/* Clear every list from the hashtable. */
	for (i = 0; i < h->size; i++)
		removeList(h->buckets[i]);
}

void printBucket(struct Hashtable *h, char bucket_number[], char option[])
{
	unsigned int bucket_id = atoi(bucket_number);
	FILE *fout;

	if (bucket_id > h->size) {
		fprintf(stderr, "[ERROR]. Bucket does not exist.\n");
	} else {

		/* Print the bucket to stdout (if no filename is provided) or */
		/* to some given file */
		if (strlen(option) == 0)
			printList(h->buckets[bucket_id], stdout);

		else {
			fout = fopen(option, "a");

			printList(h->buckets[bucket_id], fout);
			fclose(fout);
		}
	}
}

void printHash(struct Hashtable *h, char option[])
{
	int opened_file = 0, i;
	FILE *out;

	if (strlen(option) == 0)
		out = stdout;
	else {
		opened_file = 1;
		out = fopen(option, "a");
	}

	for (i = 0; i < (int)h->size; i++)
		printList(h->buckets[i], out);

	if (opened_file == 1)
		fclose(out);
}

struct Hashtable *doubleHash(struct Hashtable **h)
{
	/* Create a new hashtable with double size */
	struct Hashtable *new_hashtable = calloc(1, sizeof(struct Hashtable));
	unsigned int new_size = (*h)->size << 1, i;
	struct Node *current;

	/* Initialize the new hashtable */
	initHash(new_size, &new_hashtable);

	/* Copy every word from each bucket from the initial */
	/* hashtable to the new one; then deallocate the */
	/* memory of the first hashtable. */
	for (i = 0; i < (*h)->size; i++) {
		current = (*h)->buckets[i]->head;

		while (current != NULL) {
			addWordHash(new_hashtable, current->word);
			current = current->next;
		}

		removeList((*h)->buckets[i]);
		free((*h)->buckets[i]);
	}

	free((*h)->buckets);
	free(*h);

	return new_hashtable;
}

struct Hashtable *halveHash(struct Hashtable **h)
{
	struct Hashtable *new_hashtable = calloc(1, sizeof(struct Hashtable));
	unsigned int new_size = (*h)->size >> 1, i;
	struct Node *current;

	initHash(new_size, &new_hashtable);

	for (i = 0; i < (*h)->size; i++) {

		current = (*h)->buckets[i]->head;

		while (current != NULL) {
			addWordHash(new_hashtable, current->word);
			current = current->next;
		}

		removeList((*h)->buckets[i]);
		free((*h)->buckets[i]);
	}

	free((*h)->buckets);
	free(*h);

	return new_hashtable;
}
