#include <stdio.h>

int *gest2next (int);
int *gest1 (int);
int *gest1prev (int);
int p_end (int);

extern unsigned char *a;
extern int n;
//FUNCTIA ALLOC
int alloc (int size) {
    int * p=(int *) a;
    if ( *p==0 ) { //daca arena e goala
       if (n-4>=size+12) {
        *p=4; //indicele de start devine 4
	*(gest1(16))=0;
	*(gest1(16)+1)=0;
        *(gest1(16)+2)=size+12;
        return 16;}
       else 
	return 0;
          }
    else { //daca arena nu e goala
	
        int index=*(int*)a+12, indexblocnou, m;
	//verific daca am spatiu intre char-ul 4 si primul bloc
	int in=16;
	if (index-in>=12+size) {
	   
	    *(gest1(index)+1)=4;
	    *(gest1(in))=*(int*)a;
	    *(gest1(in)+1)=0;
	    *(int*)a=in-12;
	    *(gest1(in)+2)=size+12;
	    return in;
	
	    
	}
	while ( *(gest1(index)) != 0) { //cat timp mai exista bloc dupa
	
	    while ((m=*(gest1(index))-(index+*(gest1(index)+2)-12))>= 12+size) {
	
		indexblocnou=p_end(index)+12;

		//modific intul 2 de gestiune din blocul urmator
		*gest2next(index)=indexblocnou-12; 
		//completez intii de gestiune bloc nou
		*gest1(indexblocnou)=*gest1(index);
		*(gest1(indexblocnou)+1)=index-12;
		*(gest1(indexblocnou)+2)=12+size;
		//modific primul int de gestiune bloc curent
		*gest1(index)=indexblocnou-12;
		//printf("%d\n\n", indexblocnou);
		if (indexblocnou==16) *(int*)a=4;

		return indexblocnou;}
		
	     
	index=*gest1(index)+12; 
        }//daca nu e spatiu trec la blocul urmator
      
	indexblocnou=p_end(index)+12;
	
	if ( n-indexblocnou >= size ) {
	    *gest1(indexblocnou)=0;
	    *(gest1(indexblocnou)+1)=index-12;
	    *(gest1(indexblocnou)+2)=12+size;
	    *gest1(index)=indexblocnou-12; 
	    return indexblocnou; 
	}
	return 0;
    }
}
