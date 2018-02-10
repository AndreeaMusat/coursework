Readme 

Detalii implementare tema 2 IA 
Musat Andreea, 342C4

ugly code is ugly

util.py

	- clasa Predicate -> un predicat are un nume, o lista de variabile si o lista de domenii: variabilei de pe pozitia i ii corespunde domeniul de pe pozitia i. In plus, exista un camp is_static care este adevarat daca predicatul este unul care nu se modifica pe parcursul rularii programului (de exemplu pozitiile depozitelor, comenzile existente etc). Pentru fiecare predicat trebuie sa putem gasi atomul obtinut atunci cand fiecarei variabile i se atribuie o valoare din domeniu (functia get_instance)

	- clasa Atom -> asemanatoare unui predicat, insa aici fiecare variabila are legata o valoare. Am suprascris __eq__ si __hash__ pentru a putea verifica usor daca un atom se gaseste intr-o stare indiferent de numele variabilelor sale (adica dronePos(cell = (x, y)) se gaseste intr-un state in care exista predicatul dronePos(my_position = (x, y)))

	- clasa Operator -> este un operator STRIPS si, deci, are 2 liste de preconditii (pozitive si negative) si 2 liste de efecte (pozitive si negative), un nume, o lista de variabile (variabile care apar strict in acest operator, nu si in preconditiile sau efectele sale; de exemplu la deliver(prod_id) prod_id este variabila, insa celula in care este clientul este o variabila care apare doar in preconditii/efecte) si una de domenii. Clasa contine o metoda get_all_variables care intoarce *toate* variabilele care apar in definitia operatorului + domeniile fiecarei variabile, sub forma dictionar variabila : domeniu. Pe baza acestora, se incearca instantierea operatorului cu toate combinatiile posibile de valori si se pastreaza doar cele relevante (nu interfereaza cu starea-scop si daca au atomi statici cu mai mult de o variabila, acestia trebuie sa existe in scenariul curent)

	- clasa Action -> reprezinta un operator instantiat; are functie pentru verificare validitatii unei actiuni. In cazul unei operatii fly, ne asiguram ca celula de start si cea de end sunt diferite; in cazul tuturor actiunilor verificam ca toate predicatele statice sa existe in scenariu si ca actiunile sa fie relevante

	- clasa State -> contine o lista cu atomii adevarati din starea curenta (se presupune ca cei negativi nu sunt prezenti). Contine metode pentru determinarea relevantei unor actiuni pentru state-ul curent (se verifica ca toate efectele pozitive ale actiunii sa fie in state si niciun efect negativ sa nu fie in state), metoda pentru realizarea unei tranzitii inverse (aflarea starii din care trebuie sa pornim aplicand o actiune data pentru a ajunge in starea curenta) si pentru a verifica daca un state satisface o alta stare (starea initiala)
