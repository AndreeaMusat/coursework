# C Memory Allocator

One of my first assignments from university (~4 years ago)\
My coding style is better now, I swear!

![alt-text](https://img.devrant.com/devrant/rant/r_399333_jip2Y.jpg)

Tema are 7 fisiere sursa, astfel:
     -tema2.c contine main-ul 

     -functions.c contine functiile initialize, dump, fill si free
 	functia free elibereaza un bloc alocat, dar nu ii sterge continutul. Sunt analizate 4 cazuri: Blocul este singurul din arena, blocul este primul din arena, ultimul sau in niciunul dintre cazurile mentionate. In fiecare caz, se modifica octetii corespunzatori de gestiune de la blocul anterior (daca exista, daca nu, indexul de start) si de la blocul urmator (asemenea, daca exista).

     -alloc.c functia alloc
	functia alloc intoarce indexul primei zone in care se poate aloca un vloc avand dimensiunea ceruta. Sunt analizate mai multe cazuri: daca arena este goala, atunci blocul va incepe pe pozitia 16. Daca arena nu este goala, atunci se testeaza daca exista spatiu intre indexul de start si primul bloc. Daca nu, se testeaza daca exista spatiu intre blocurile alocate pana atunci. In caz contrar, blocul nou va fi alocat la sfarsitul arenei. (Blocul se aloca numai in cazul in care dimensiunea permite asta)

     -show.c functiile show free, shoe usage si show allocations

     -test_functions.c contine functii de test (daca blocul cu index-ul dat ca parametru este primul sau ultimul) si functii care intorc pointeri la octetii de gestiune

     -cnt_functions.c contine functii care numara octetii liberi, blocurile libere, nr de blocuri alocate, nr de octeti folositi si functii care calculeaza eficienta si fragmentarea

     -execute.c este functia are citeste comenzile si le interpreteaza
	Cat timp nu a fost citita linia FINALIZE, functia citeste o linie noua, desparte linia in cuvinte, iar apoi, in functie de primul cuvant, se apeleaza functia potrivita, iar apoi se citeste o noua linie.

