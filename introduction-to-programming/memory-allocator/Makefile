build: allocator

allocator: alloc.o cnt_functions.o execute.o functions.o show.o tema2.o test_functions.o
	gcc -o allocator alloc.o cnt_functions.o execute.o functions.o show.o tema2.o test_functions.o -Wall

alloc.o: alloc.c
	gcc -c -o alloc.o alloc.c -Wall

cnt_functions.o: cnt_functions.c
	gcc -c -o cnt_functions.o cnt_functions.c -Wall
execute.o: execute.c
	gcc -c -o execute.o execute.c -Wall
functions.o: functions.c
	gcc -c -o functions.o functions.c -Wall
show.o: show.c
	gcc -c -o show.o show.c -Wall
tema2.o: tema2.c
	gcc -c -o tema2.o tema2.c -Wall
test_functions.o: test_functions.c
	gcc -c -o test_functions.o test_functions.c -Wall
clean:
	rm *.o allocator
 
