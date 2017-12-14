
# coding: utf-8

# # Logica cu predicate (2). Rezoluție
#  - Andrei Olaru
#  - Tudor Berariu
# 

# ## Scopul laboratorului
# 
# Familiarizarea cu mecanismul rezoluției și cu strategiile de rezoluție.
# 
# #### Resurse
# 
# Cursul 5 de IA slides 34-44.

# ### Cerința 1
# 
# * din notebook-ul de la Laboratorul 5 faceți Download as &rarr; Python și salvați fișierul ca `Lab05.py`, în acest director.
# * adăugați de asemenea în acest director fișierul `Lab05tester.py` (**descărcați din nou** de pe site).

# In[2]:

# TODO
from Lab05tester import *
from Lab05 import *


# In[3]:

from copy import deepcopy
from functools import reduce

# în această celulă se găsesc câteva funcții utilizate intern

dummy = make_atom("P")
[and_name, or_name, neg_name] = [get_head(s) for s in [make_and(dummy, dummy), make_or(dummy, dummy), make_neg(dummy)]]
def pFail(message, f):
    print(message + " <" + str(f) + ">")
    return False
def check_term(T):
    if is_constant(T):
        return (get_value(T) is not None) or pFail("The value of the constant is None", T)
    if is_variable(T):
        return (get_name(T) is not None) or pFail("The name of the variable is None", T)
    if is_function_call(T):
        return not [t for t in get_args(T) if not check_term(t)] and             (get_head(T) is not None or pFail("Function is not callable", T))
    return pFail("Term is not one of constant, variable or function call", T)
def check_atom(A):
    if is_atom(A):
        return not [t for t in get_args(A) if not check_term(t)] and             (get_head(A) is not None or pFail("Predicate name is None", A))
    return pFail("Is not an atom", A)
def check_sentence(S):
    if is_atom(S):
        return check_atom(S)
    if is_sentence(S):
        if get_head(S) in [and_name, or_name]:
            return (len(get_args(S)) >= 2 or pFail("Sentence has too few operands", S))                 and not [s for s in get_args(S) if not check_sentence(s)]
        if get_head(S) == neg_name:
            return (len(get_args(S)) == 1 or pFail("Negative sentence has not just 1 operand", S))                 and check_sentence(get_args(S)[0])
    return pFail("Not sentence or unknown type", S)

def add_statement(kb, conclusion, *hypotheses):
    s = conclusion if not hypotheses else make_or(*([make_neg(s) for s in hypotheses] + [conclusion]))
    if check_sentence(s):
        kb.append(s)
        print("OK: Added statement " + print_formula(s, True))
        return True
    print("-- FAILED CHECK: Sentence does not check out <"+print_formula(s, True)+"><" + str(s) + ">")
    return False

var_no = 0;

def assign_next_var_name():
    global var_no
    var_no += 1
    return "v" + str(var_no)

def gather_vars(S):
    return [get_name(S)] if is_variable(S) else         [] if not has_args(S) else reduce(lambda res, a: res + gather_vars(a), get_args(S), [])

def make_unique_var_names(KB):
    global var_no
    var_no = 0
    return [substitute(S, {var: make_var(assign_next_var_name()) for var in gather_vars(S)}) for S in KB]           
            
def print_KB(KB):
    print("KB now:")
    for s in KB:
        print("\t\t\t" + print_formula(s, True))


# In[4]:

# KB 1
# based on an example in Artificial Intelligence - A Modern Approach
KB_America = []
#0 Mr West is a US general
add_statement(KB_America, make_atom("USGeneral", make_const("West")))
#1 General Awesome is also a US general
add_statement(KB_America, make_atom("USGeneral", make_const("General_Awesome")))
#2 General Awesome is Awesome
add_statement(KB_America, make_atom("Awesome", make_const("General_Awesome")))
#3 Nono is an enemy of America
add_statement(KB_America, make_atom("Enemy", make_const("Nono"), make_const("America")))
#4 M1 is a type of missile
add_statement(KB_America, make_atom("Missile", make_const("M1")))
#5 Nono has the M1 missile
add_statement(KB_America, make_atom("Owns", make_const("Nono"), make_const("M1")))

#6 any US general is an American
add_statement(KB_America, make_atom("American", make_var("x")), make_atom("USGeneral", make_var("x")))
#7 any missle is a weapon
add_statement(KB_America, make_atom("Weapon", make_var("x")), make_atom("Missile", make_var("x")))
#8 if anyone owns a missile, it is General West that sold them that missile
add_statement(KB_America, make_atom("Sells", make_const("West"), make_var("y"), make_var("x")), make_atom("Owns", make_var("x"), make_var("y")), make_atom("Missile", make_var("y")))
#9 any American who sells weapons to a hostile is a criminal
add_statement(KB_America, make_atom("Criminal", make_var("x")), make_atom("Weapon", make_var("y")), make_atom("Sells", make_var("x"), make_var("y"), make_var("z")), make_atom("Hostile", make_var("z")), make_atom("American", make_var("x")))
#10 any enemy of America is called a hostile
add_statement(KB_America, make_atom("Hostile", make_var("x")), make_atom("Enemy", make_var("x"), make_const("America")))
#11 America is awesome if at least an American is awesome
add_statement(KB_America, make_atom("Awesome", make_const("America")), make_atom("American", make_var("x")), make_atom("Awesome", make_var("x")))

KB_America = make_unique_var_names(KB_America)

print_KB(KB_America)


# In[5]:

# KB 2
# din cursul de IA
KB_Faster = []

def the_greyhound():
    return make_const("Greg")

#0 horses are faster than dogs
add_statement(KB_Faster, make_atom("Faster", make_var("x"), make_var("y")), make_atom("Horse", make_var("x")), make_atom("Dog", make_var("y")))
#1 there is a greyhound that is faster than any rabbit
add_statement(KB_Faster, make_atom("Faster", make_function_call(the_greyhound), make_var("z")), make_atom("Rabbit", make_var("z")))
#2 Harry is a horse
add_statement(KB_Faster, make_atom("Horse", make_const("Harry")))
#3 Ralph is a rabbit
add_statement(KB_Faster, make_atom("Rabbit", make_const("Ralph")))
#4 Greg is a greyhound
add_statement(KB_Faster, make_atom("Greyhound", make_function_call(the_greyhound)))
#5 A greyhound is a dog
add_statement(KB_Faster, make_atom("Dog", make_var("y")), make_atom("Greyhound", make_var("y")))
#6 transitivity
add_statement(KB_Faster, make_atom("Faster", make_var("x"), make_var("z")),
              make_atom("Faster", make_var("x"), make_var("y")), make_atom("Faster", make_var("y"), make_var("z")))

KB_Faster = make_unique_var_names(KB_Faster)

print_KB(KB_Faster)


# In[6]:

KB_test = []
add_statement(KB_test, make_atom("Q", make_var("x")), make_atom("P", make_var("x")))
add_statement(KB_test, make_atom("P", make_const("A")))

KB_test = make_unique_var_names(KB_test)
print_KB(KB_test)


# ### Cerința 2
# 
# * Implementați funcția `resolves`, care primește două clauze (literali sau disjuncții de literali) și întoarce `False` dacă cele două clauze nu rezolvă, altfel un tuplu care conține literalii care rezolvă, din cele două clauze, și substituția sub care aceștia rezolvă.

# In[7]:

def is_positive_literal(L):
    return is_atom(L)
def is_negative_literal(L):
    global neg_name
    return get_head(L) == neg_name and is_positive_literal(get_args(L)[0])
def is_literal(L):
    return is_positive_literal(L) or is_negative_literal(L)

def resolves(C1, C2):
    print("testing " + print_formula(C1, True) + " and " + print_formula(C2, True))
 
    literals_C1 = []
    literals_C2 = []
    
    if is_literal(C1):
        literals_C1 = [C1]
    else:
        literals_C1 = get_args(C1)
        
    if is_literal(C2):
        literals_C2 = [C2]
    else:
        literals_C2 = get_args(C2)
        
    for lit1 in literals_C1:
        for lit2 in literals_C2:
            if is_positive_literal(lit1) and is_negative_literal(lit2):
                res = unify(lit1, get_args(lit2)[0])
                if res is not False:
                    return (lit1, lit2, res)
                
            if is_negative_literal(lit1) and is_positive_literal(lit2):
                res = unify(get_args(lit1)[0], lit2)
                if res is not False:
                    return (lit1, lit2, res)
                
    # întoarce un tuplu (literal-din-C1, literal-din-C2, substituție)
    # unde literal-din-C1 și literal-din-C2 unifică sub substituție
    return False

# Test!
test_batch(4, globals())


# In[8]:

# prints a 5-tuple resolvent representation (see below)
def print_r(R):
    if R is None:
        print("no resolvent")
    else:
        print("resolvent: " + print_formula(R[2], True) + "/" + print_formula(R[3], True) + str(R[4])                         + "\n\t\t in " + print_formula(R[0], True) + "\n\t\t and " + print_formula(R[1], True))


# ### Cerința 3
# 
# * implementați partea lipsă din funcția `solve_problem`, utilizând o strategie de rezoluție la alegere pentru a alege două clauze care rezolvă, și adăugând rezultatul pasului de rezoluție la baza de cunoștințe.

# In[39]:

def sort_function(clause):
    if is_literal(clause):
        return 1
    else:
        return len(get_args(clause))
    
def solve_problem(hypotheses, conclusion):
    KB = hypotheses[:]
    KB = [make_neg(conclusion)] + KB # puteți adăuga și la sfârșit (în funcție de strategie)
    Effort = 50
    
    seen = []
    
    while Effort > 0:
    
        KB = sorted(KB, key=sort_function)
        
        found_resolvent = False
        res = None
        
        for i in range(len(KB)):
            for j in range(len(KB)):
                if i == j or (KB[i], KB[j]) in seen or (KB[j], KB[i]) in seen:
                    continue
                res = resolves(KB[i], KB[j])
                if res != False:
                    seen.append((KB[i], KB[j]))
                    found_resolvent = True
                    break
            if found_resolvent:
                break
        
        resolvent = None
        
        if res is not None:
            # Se calculează un rezolvent, ca tuplu (Clauza1, Clauza2, Literal-din-clauza1, Literal-din-clauza2, substituție)
            resolvent = (KB[i], KB[j], res[0], res[1], res[2])
    
            print_r(resolvent)
        
        if resolvent is None:
            print("Failed. No resolving clauses. Effort left " + str(Effort))
            return False
        
        # Se calculează noua clauză de adăugat și se adaugă la baza de cunoștințe
        # Clauza trebuie să fie în acest punct o listă de literali
        C = []
        
        KBi_literals = get_args(KB[i]) if not is_literal(KB[i]) else [KB[i]]
        KBj_literals = get_args(KB[j]) if not is_literal(KB[j]) else [KB[j]]
       
        for kbi_literal in KBi_literals:
            if kbi_literal == res[0]: 
                continue
            else:
                C.append(kbi_literal)
                
        for kbj_literal in KBj_literals:
            if kbj_literal == res[1]: 
                continue
            else:
                C.append(kbj_literal)
        
        C = list(map(lambda x : substitute(x, res[2]), C))

        # update KB
        if C == []:
            print("Done (effort left " + str(Effort) + ")")
            return True
        if len(C) == 1:
            C = C[0]
        else:
            C = make_or(*C)
            
        print("Added: " + print_formula(C, True))
        KB = [C] + KB
        Effort -= 1

        print_KB(KB)
    print("Failed. Effort exhausted.")
                
        
#print_KB(KB_test)
# solve_problem(deepcopy(KB_test), make_atom("Q", make_const("A")))

#print_KB(KB_America)
# solve_problem(deepcopy(KB_America), make_atom("Criminal", make_const("West")))

#print_KB(KB_Faster)
solve_problem(deepcopy(KB_Faster), make_atom("Faster", make_const("Harry"), make_const("Ralph")))


# In[ ]:


