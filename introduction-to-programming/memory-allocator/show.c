#include <stdio.h>

int *gest2next (int);
int *gest1 (int);
int *gest1prev (int);
int p_end (int);
int nr_oct_lib();
int nr_bloc_lib();
int nr_blocuri();
int nr_oct_fol ();
float efic();
float fragm ();

extern unsigned char *a;
extern int n;

//SHOW USAGE
void show_usage() {
    printf("%d blocks (%d bytes) used\n", nr_blocuri(), nr_oct_fol());
    printf("%d%% efficiency\n", (int)(100*efic()));
    printf("%d%% fragmentation\n", (int)(100*fragm()));
   }
//SHOW FREE
void show_free() {
    if (*(int*)a==0) printf("1 blocks (%d bytes) free\n", n-4);
    else printf("%d blocks (%d bytes) free\n", nr_bloc_lib(), nr_oct_lib());
}

//SHOW ALLOCATIONS
void show_alloc () {
    if (*(int*)a==0) printf("OCCUPIED 4 bytes\nFREE %d bytes\n", n-4);
    else { int spliber;
	printf("OCCUPIED 4 bytes\n");
	int index=*(int*)a+12;	
	    if (index>16) {
		printf("FREE %d bytes\n", index-16);
		while ( *gest1(index) != 0 ) {
                     printf("OCCUPIED %d bytes\n", *(gest1(index)+2));
                     spliber=*(gest1(index))-(index+*(gest1(index)+2)-12);
                     if(spliber) printf("FREE %d bytes\n", spliber);
                     index=*gest1(index)+12;}
		printf("OCCUPIED %d bytes\n", *(gest1(index)+2));
                  if (p_end(index) < n)
                          printf("FREE %d bytes\n", n-p_end(index));

 	    }

	    else { 
		while ( *gest1(index) != 0 ) {
		   printf("OCCUPIED %d bytes\n", *(gest1(index)+2));
          	   spliber=*(gest1(index))-(index+*(gest1(index)+2)-12);
	  	   if(spliber) printf("FREE %d bytes\n", spliber);
		   index=*gest1(index)+12;}
		printf("OCCUPIED %d bytes\n", *(gest1(index)+2));
		if (p_end(index) < n) 
			printf("FREE %d bytes\n", n-p_end(index));
	    }
    }
}
