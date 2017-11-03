build: filtru

filtru: image_processing.cpp image_processing.h pgm_image.h
	mpic++ -o filtru image_processing.cpp
run: 
	mpirun -np 12 ./filtru topologie.in imagini.in statistica.out
clean: 
	rm filtru
