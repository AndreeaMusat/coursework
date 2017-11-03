export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.

build: tema1

tema1: tema1.o list.o hashtable.o 
	gcc -std=c89 tema1.o list.o hashtable.o -o tema1 -Wall -lhash -L.

tema1.o: tema1.c
	gcc -std=c89 tema1.c -c -o tema1.o -Wall

list.o: list.c
	gcc -std=c89 list.c -c -o list.o -Wall

hashtable.o: hashtable.c
	gcc -std=c89 hashtable.c -c -o hashtable.o -Wall

clean:
	rm tema1 *.o
