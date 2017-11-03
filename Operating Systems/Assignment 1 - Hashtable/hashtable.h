/* Author: Andreea-Alexandra Musat, 333CA */

#pragma once
#include "list.h"
#include "hash.h"

struct Hashtable {
	unsigned int size;
	struct LinkedList **buckets;
};

/* initialize the hashtable: allocate memory for the buckets */
/* and set the size */
void initHash(unsigned int size, struct Hashtable **h);

/* add a word in the corresponding bucket */
void addWordHash(struct Hashtable *h, char word[]);

/* remove a word from the hashtable if it exists */
void removeWordHash(struct Hashtable *h, char word[]);

/* find wether a given word is in the hashtable */
void findWordHash(struct Hashtable *h, char word[], char option[]);

/* clear the hashtable */
void clearHash(struct Hashtable *h);

/* print one bucket (= linked list) from the hashtable */
void printBucket(struct Hashtable *h, char bucket_number[], char option[]);

/* print the entire hashtable */
void printHash(struct Hashtable *h, char option[]);

/* reallocate the hashtable so that it doubles its size */
struct Hashtable *doubleHash(struct Hashtable **h);

/* reallocate the hashtable so that it halves its size */
struct Hashtable *halveHash(struct Hashtable **h);
