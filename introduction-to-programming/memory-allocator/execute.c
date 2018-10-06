#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define DIM 20

void show_free();
void show_alloc();
void show_usage();
void initialize();
void dump();
void fill (int, int, int);
void free_a(int);
int alloc(int);


extern unsigned char *a;
extern int n;

void execute () {
    char *str=NULL, **mat, *tok=NULL;
    int i;
    //aloc dinamic spatiu pentru s si pentru matricea in care retin cuv
    str = (char *) calloc (DIM, sizeof(char));
    mat = (char **) calloc (4, sizeof(char*)); //matr are max 4 cuv
   
    fgets(str,DIM,stdin); //citesc prima linie
    while ( str != NULL) {//cat timp nu a citit finalize
	//despart linia citita in cuvinte
	tok=strtok(str, " \n");
	i=0;
	while ( tok != NULL ) {
	    mat[i]=strdup(tok);
	    i++;
	    tok=strtok(NULL," \n");
	    }
	if(strcmp(mat[0],"INITIALIZE")==0) {
		    
		    n=atoi(mat[1]);
		    initialize(n);
		    }
	if(strcmp(mat[0], "DUMP")==0) {
		    dump();
		    }
	if (strcmp(mat[0], "FREE")==0) {
		    free_a(atoi(mat[1]));
		    }
	if (strcmp(mat[0],  "ALLOC")==0)  {
		    int b;
		    b=alloc(atoi(mat[1]));
		    printf("%d\n", b);
		    }
	if (strcmp(mat[0], "FILL")==0) {
		    fill(atoi(mat[1]),atoi(mat[2]),atoi(mat[3]));
		    }
	if (strcmp(mat[0], "SHOW")==0) {
			
			if(strcmp(mat[1], "FREE")==0) {
				    show_free();  }
			if(strcmp(mat[1], "USAGE")==0) {
				    show_usage(); }
			if(strcmp(mat[1], "ALLOCATIONS")==0) {
				    show_alloc(); }
			}	
	if (strcmp(mat[0], "FINALIZE")==0) break;
           fgets(str, DIM, stdin);
}       //eliberare memorie
	free(str);
	for (i=0; i<=3; i++) free(mat[i]);
	free(mat);

}
