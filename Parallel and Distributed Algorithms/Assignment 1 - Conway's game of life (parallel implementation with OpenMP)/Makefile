serial: g_serial.c
	gcc -o g_serial g_serial.c -Wall -g

parallel: g_omp.c
	gcc -o g_omp -fopenmp g_omp.c -Wall -g

clean:
	rm g_serial g_omp out*.txt