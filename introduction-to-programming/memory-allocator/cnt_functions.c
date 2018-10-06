#include <stdio.h>

extern unsigned char *a;
extern int n;

int islast (int);
int isfirst (int);
int *gest1 (int);
int p_end (int);

// FUNCTIE CARE INTOARCE NR DE OCTETI LIBERI DIN ARENA
int nr_oct_lib() {
    if (*(int*)a==0) return n;
    else {
    int index=*(int*)a+12, spliber=0;
    if (index>16) spliber+=index-16;
    while ( *gest1(index) != 0 ) {
	spliber+=*(gest1(index))-(index+*(gest1(index)+2)-12);
	index=*gest1(index)+12;}
    spliber+=n-p_end(index);
    return spliber;} 
}

//FUNCTIE CARE INTOARCE NR DE BLOCURI LIBERE DIN ARENA
int nr_bloc_lib() {
    if (*(int*)a==0) return 1;
    else {
    int index=*(int*)a+12, cont=0, spliber;
    if (index>16) cont++;
    while ( *gest1(index) != 0 ) {
	spliber=*(gest1(index))-(index+*(gest1(index)+2)-12);
	if (spliber) cont++;
	index=*gest1(index)+12;}	
    if (p_end(index)<n) cont++;
   return cont;} 
}

//FUNCTIE CARE INTOARCE NR DE BLOCURI ALOCATE DIN ARENA
int nr_blocuri() {
    if (*(int*)a==0) return 0;
    else {
    int index=*(int*)a+12, nr=1;
    while ( *gest1(index) != 0) {
	nr++;
	index=*gest1(index)+12;}
    return nr;} 
}

//FUNCTIE CARE INTOARCE NR DE OCTETI FOLOSITI DIN ARENA
int nr_oct_fol () {
    if (*(int*)a==0) return 0;
    else return n-nr_oct_lib()-12*nr_blocuri()-4;
}

//FUNCTIE CARE INTOARCE EFICIENTA
float efic() {
    float f;
    f=(float) nr_oct_fol() / (4+ nr_oct_fol() + 12*nr_blocuri() );
    return f;
}

//FUNCTIE CARE INTOARCE FRAGMENTAREA
float fragm () {
    if (*(int*)a==0) return 0;
    else {
    float f;
    f=(float) (nr_bloc_lib()-1)/nr_blocuri();
    return f;}
}
