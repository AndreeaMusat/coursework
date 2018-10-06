#include <stdio.h>
#include <stdlib.h>

int islast (int);
int isfirst (int);
int *gest2next (int);
int *gest1 (int);
int *gest1prev (int);
int p_end (int);

extern unsigned char *a;
extern int n;

//FUNCTIA INITIALIZE
void initialize (int m) {
    a = (unsigned char *) calloc ( m , sizeof(unsigned char));
    return ;
}

//FUNCTIA DUMP
void dump() {
    int i;
    unsigned char *p;
    p = a; //p pointeaza la primul element din arena
    for (i=0; i<n;i++) {
	if (i%16==0) printf("%08X\t", i);
	else 
		if (i%8==0) printf(" ");
	printf("%02X%s", p[i], ((i+1)%16==0)?" \n":" ");	
    }
    printf("\n%08X\n", n); 
}

//FUNCTIA FILL
void fill(int index, int size, int value) {
    unsigned char *p;
    int i;
    p = &a[index]; //p ia adresa componentei de pe pozitia index
    for (i=0; i<size; i++) { //incepand cu elementul de pe pozitia index
	*(p+i)=value;//size componente consecutive iau valoarea value
    }
}

//FUNCTIA FREE
void free_a(int index) {
    if (isfirst(index)==1) { //daca blocul e primul dar nu ultimul
	if (islast(index)==0) {
	    *(gest2next(index))=0;
	    *(int *)a=*gest1(index);
	    
	}
	else *(int*)a=0; //daca blocul e singur   
    } 
    else { //daca blocul nu e primul
	if (islast(index)==0) { //daca nu e ultimul
	    *(gest1prev(index))=*(gest1(index)); 
	    *(gest2next(index))=*(gest1(index)+1);
	    }
	else { //daca este ultimul
	    *(gest1prev(index))=0;
	    }
    }
}


