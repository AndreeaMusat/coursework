#include <stdio.h>
#include <stdlib.h>

extern unsigned char *a;
extern int n;
//intoarce pointer la primul int de gestiune al blocului curent
int * gest1 (int index) {
    return (int*)(a+index-12);
}


//det daca blocul care incepe la index este primul
int isfirst (int index) {
    if(*(gest1(index)+1)==0) return 1;
    else return 0;
}

//det daca blocul care incepe la index este ultimul
int islast (int index) {
    if (*(gest1(index))==0) return 1;
    else return 0;
}

//intoarce pointer la al doilea int de gestiune din blocul urmator
int * gest2next(int index) {
    int *p=gest1(index); //pointer la primul int de gestiune bloc curent
    int k=*p;//k=indice start bloc urmator
    return (int*)(a+k)+1;
}

// intoarce pointer la primul int de gestiune din blocul anterior
int * gest1prev(int index) {
    int *p=gest1(index)+1; //pointer la al doilea int de gestiune bloc curent
    int k=*p;//k=indice start bloc anterior
    return (int*)(a+k);
}


// intoarce indexul sfarsitului blocului care incepe la index (zona utilizator)
int  p_end (index) {
     int m=*(gest1(index)+2);
     return index+m-12;
     }
