
# coding: utf-8

# # Logica cu predicate (1). Reprezentare & Unificare
#  - Andrei Olaru
#  - Tudor Berariu
# 

# ## Scopul laboratorului
# 
# Scopul acestui laborator este familiarizarea cu reprezentarea logică a cunoștințelor și cu mecanismele de lucru cu cunoștințe reprezentate prin logica cu predicate de ordinul I (LPOI / FOPL).
# 
# În cadrul laboratorului, va fi necesar să vă alegeți o reprezentare internă pentru elementele din FOPL, și apoi să implementați procesul de unificare între două formule din logica cu predicate. 
# 
# 
# #### Resurse
# 
# * Cursul 5 de IA, slides 25-27
# * https://en.wikipedia.org/wiki/Unification_(computer_science)#Examples_of_syntactic_unification_of_first-order_terms
# * algoritmul lui Robinson (vezi pdf)
# 

# ## Reprezentare
# 
# În LPOI trebuie să putem reprezenta următoarele elemente:
# * _termen_ -- poate fi luat ca argument de către un predicat. Un termen poate fi:
#   * o constantă -- are o valoare
#   * o variabilă -- are un nume și poate fi legată la o valoare
#   * un apel de funcție -- are numele funcției și argumentele (e.g. add[1, 2, 3]). Se evaluează la o valoare. Argumentele funcției sunt tot termeni.
#     * Notă: În text vom scrie apelurile de funcții cu paranteze drepte, pentru a le deosebi de atomi.
# * _formulă (propoziție) logică_ -- se poate evalua la o valoare de adevăr, într-o interpretare (o anumită legare a numelor la o semantică). O formulă poate fi:
#   * un atom -- aplicarea unui predicat (cu un nume) peste o serie de termeni (argumentele sale)
#   * negarea unei formule
#   * un conector logic între două propoziții -- conjuncție sau disjuncție
#   
# 
# ### Cerința 1
# 
# Creați o reprezentare internă pentru formule logice. Pentru această reprezentare, vom avea:
# * o serie de funcții care o construiesc -- `make_*` și `replace_args`
# * o serie de funcții care o verifică -- `is_*`
# * o serie de funcții care accesează elementele din reprezentare -- `get_*`
# 
# 
# **Important:** Pentru a lucra mai ușor cu formulele, vom considera că pentru apelurile de funcții și pentru toate formulele (atât atomi cât și propoziții compuse), reprezentarea are un _head_ (după caz, numele funcției, numele predicatului, sau conectorul logic) și o listă de argumente (după caz, lista de argumente a funcției, lista de argumente a predicatului, o listă cu propoziția negată, sau lista de propoziții unite de conectorul logic (2 sau mai multe)).
# 
# **Notă:** la început, implementați funcțiile de verificare ca și cum argumentele date are fi reprezentate corect (deci doar pentru a deosebi între diversele tipuri de reprezentare). Ulterior, verificați și ca argumentele date să fie într-adevăr corect reprezentate.

# In[53]:

from operator import add
from Lab05tester import test_batch
from copy import deepcopy

# In[54]:

### Reprezentare - construcție

CONST = 0
VAR = 1
FUNC = 2
PRED = 3
NEG = 4
AND = 5
OR = 6

# întoarce un termen constant, cu valoarea specificată.
def make_const(value):
    return (CONST, [value])

# întoarce un termen care este o variabilă, cu numele specificat.
def make_var(name):
    return (VAR, [name])

# întoarce un termen care este un apel al funcției specificate, pe restul argumentelor date.
# E.g. pentru a construi termenul add[1, 2, 3] vom apela make_function_call(add, 1, 2, 3)
# !! ATENȚIE: python dă args ca tuplu cu restul argumentelor, nu ca listă. Se poate converti la listă cu list(args)
def make_function_call(function, *args):
    return (FUNC, [function, list(args)])

# întoarce o formulă formată dintr-un atom care este aplicarea predicatului dat pe restul argumentelor date.
# !! ATENȚIE: python dă args ca tuplu cu restul argumentelor, nu ca listă. Se poate converti la listă cu list(args)
def make_atom(predicate, *args):
    return (PRED, [predicate, list(args)])

# întoarce o formulă care este negarea propoziției date.
# get_args(make_neg(s1)) va întoarce [s1]
def make_neg(sentence):
    return (NEG, [sentence])

# întoarce o formulă care este conjuncția propozițiilor date (2 sau mai multe).
# e.g. apelul make_and(s1, s2, s3, s4) va întoarce o structură care este conjuncția s1 ^ s2 ^ s3 ^ s4
#  și get_args pe această structură va întoarce [s1, s2, s3, s4]
def make_and(sentence1, sentence2, *others):
    return (AND, [sentence1, sentence2] + list(others))

# întoarce o formulă care este disjuncția propozițiilor date.
# e.g. apelul make_or(s1, s2, s3, s4) va întoarce o structură care este disjuncția s1 V s2 V s3 V s4
#  și get_args pe această structură va întoarce [s1, s2, s3, s4]
def make_or(sentence1, sentence2, *others):
    return (OR, [sentence1, sentence2] + list(others))

# întoarce o copie a formulei sau apelul de funcție date, în care argumentele au fost înlocuite
#  cu cele din lista new_args.
# e.g. pentru formula p(x, y), înlocuirea argumentelor cu lista [1, 2] va rezulta în formula p(1, 2).
# Noua listă de argumente trebuie să aibă aceeași lungime cu numărul de argumente inițial din formulă.
def replace_args(formula, new_args):
    if is_function_call(formula) or is_atom(formula):
        return (formula[0], [formula[1][0], new_args])
    else:
        return (formula[0], new_args)
    
    
### Reprezentare - verificare

# întoarce adevărat dacă f este un termen.
def is_term(f):
    return is_constant(f) or is_variable(f) or is_function_call(f)

# întoarce adevărat dacă f este un termen constant.
def is_constant(f):
    return f[0] == CONST

# întoarce adevărat dacă f este un termen ce este o variabilă.
def is_variable(f):
    return f[0] == VAR

# întoarce adevărat dacă f este un apel de funcție.
def is_function_call(f):
    return f[0] == FUNC

# întoarce adevărat dacă f este un atom (aplicare a unui predicat).
def is_atom(f):
    return f[0] == PRED

# întoarce adevărat dacă f este o propoziție validă.
def is_sentence(f):
    return f[0] == OR or f[0] == AND or f[0] == NEG or is_atom(f)

# întoarce adevărat dacă formula f este ceva ce are argumente.
def has_args(f):
    return is_function_call(f) or is_sentence(f)

### Reprezentare - verificare

# pentru constante (de verificat), se întoarce valoarea constantei; altfel, None.
def get_value(f):
    if is_constant(f):
        return f[1][0]
    return None

# pentru variabile (de verificat), se întoarce numele variabilei; altfel, None.
def get_name(f):
    if is_variable(f):
        return f[1][0]
    return None

# pentru apeluri de funcții, se întoarce conversia în șir de caractere a referinței la funcție;
# pentru atomi, se întoarce numele predicatului; 
# pentru propoziții compuse, se întoarce un șir de caractere care reprezintă conectorul logic (e.g. ~, A sau V);
# altfel, None
def get_head(f):
    if is_function_call(f) or is_atom(f):
        return str(f[1][0])
    elif is_sentence(f):
        if f[0] == NEG:
            return "~"
        elif f[0] == OR:
            return "V"
        elif f[0] == AND:
            return "A"
    return None

# pentru propoziții sau apeluri de funcții, se întoarce lista de argumente; altfel, None.
# Vezi și "Important:", mai sus.
def get_args(f):
    # print(f[1])
    if is_function_call(f):
        return f[1][1]
    elif is_sentence(f) and not is_atom(f):
        return f[1]
    elif is_atom(f):
        return f[1][1]
    else:
        return None

get_args(make_and(make_atom('P', make_var('X')), make_atom('Q', make_const('5'))))
test_batch(0, globals())


# In[55]:

# Afișează formula f. Dacă argumentul return_result este True, rezultatul nu este afișat la consolă, ci întors.
def print_formula(f, return_result = False):
    ret = ""
    if is_term(f):
        if is_constant(f):
            ret += str(get_value(f))
        elif is_variable(f):
            ret += "?" + get_name(f)
        elif is_function_call(f):
            ret += get_head(f) + "[" + "".join([print_formula(arg, True) + "," for arg in get_args(f)])[:-1] + "]"
        else:
            ret += "???"
    elif is_atom(f):
        ret += get_head(f) + "(" + "".join([print_formula(arg, True) + ", " for arg in get_args(f)])[:-2] + ")"
    elif is_sentence(f):
        # negation, conjunction or disjunction
        args = get_args(f)
        if len(args) == 1:
            ret += get_head(f) + print_formula(args[0], True)
        else:
            ret += "(" + get_head(f) + "".join([" " + print_formula(arg, True) for arg in get_args(f)]) + ")"
    else:
        ret += "???"
    if return_result:
        return ret
    print(ret)
    return
    
# Verificare construcție și afișare
# Ar trebui ca ieșirea să fie similară cu: (A (V ~P(?x) Q(?x)) T(?y, <built-in function add>[1,2]))
formula1 = make_and(
    make_or(make_neg(make_atom("P", make_var("x"))), make_atom("Q", make_var("x"))),
    make_atom("T", make_var("y"), make_function_call(add, make_const(1), make_const(2))))
print_formula(formula1)


# ## Unificare
# 
# Unificarea a două formule logice ce conțin variabile înseamnă găsirea unei substituții astfel încât aplicarea acesteia pe cele două formule să rezulte în două formule identice.
# 
# O substituție conține asocieri de variabile la termeni. La aplicarea unei substituții, variabilele care apar în substituție sunt înlocuite, în formulă, cu termenii asociați, până când nu se mai poate face nicio înlocuire.

# In[56]:

# Aplică în formula f toate elementele din substituția dată și întoarce formula rezultată
def substitute(f, substitution):
    if substitution is None:
        return None
    if is_variable(f) and (get_name(f) in substitution):
        return substitute(substitution[get_name(f)], substitution)
    if has_args(f):
        return replace_args(f, [substitute(arg, substitution) for arg in get_args(f)])
    return f

def test_formula(x, copyy = False):
    fun = make_function_call(add, make_const(1), make_const(2))
    return make_and(make_or(make_neg(make_atom("P", make_const(x))), make_atom("Q", make_const(x))),                     make_atom("T", fun if copyy else make_var("y"), fun))

# Test (trebuie să se vadă efectele substituțiilor în formulă)
test_batch(1, globals())


# ### Cerința 2
# 
# Implementați funcțiile `occur_check` și `unify`, conform algoritmului lui Robinson (vezi pdf).

# In[57]:

# Verifică dacă variabila v apare în termenul t, având în vedere substituția subst.
# Întoarce True dacă v apare în t (v NU poate fi înlocuită cu t), și False dacă v poate fi înlocuită cu t.
def occur_check(v, t, subst):
    if v == t:
        return True
    
    elif get_name(t) in subst.keys():
        return occur_check(v, substitute(t, subst), subst)
    
    elif is_function_call(t):
        ans = False
        for arg in get_args(t):
            ans |= occur_check(v, arg, subst)
        return ans
    else:
        return False

# Test!
test_batch(2, globals())


# In[58]:

# Unifică formulele f1 și f2, sub o substituție existentă subst.
# Rezultatul unificării este o substituție (dicționar nume-variabilă -> termen),
#  astfel încât dacă se aplică substituția celor două formule, rezultatul este identic.
def unify(f1, f2, psubst = None):
    stack = []
    s = f1
    t = f2
    stack.append((s,t))
    if psubst is None:
        psubst = {}
    subst = deepcopy(psubst)
    while stack:
        (s,t) = stack.pop()
        while s in list(subst.keys()):
            s = substitute(s, subst)
        while t in list(subst.keys()):
            t = substitute(t, subst)
            
        if s != t:
            if is_variable(s):
                if occur_check(s,t,subst):
                    return False
                else:
                    subst[get_name(s)] = t
                    
            elif is_variable(t):
                if occur_check(t,s, subst):
                    return False
                else:
                    subst[get_name(t)] = s
                    
            elif (is_function_call(s) and is_function_call(t)) or (is_atom(s) and is_atom(t)):
                
                if get_head(s) == get_head(t):
                    for idx in range(len(get_args(s))):
                        stack.append((get_args(s)[idx], get_args(t)[idx]))
                else:
                    return False

            else:
                return False
    return subst

# Test!
test_batch(3, globals())


# In[ ]:


