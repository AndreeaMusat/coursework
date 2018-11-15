% 1. maximum of two numbers.
% maximum(Number1, Number2, Result).
maximum(X, Y, Z) :- X >= Y, Z is X.
maximum(X, Y, Z) :- X < Y, Z is Y.


% 2.1 member.
% isMember(Element, List).
isMember(Elem, [Elem|_]).
isMember(Elem, [_|Rest]) :- isMember(Elem, Rest).


% 2.2 concat.
% concat(List1, List2, ResultingList).
concat([], L2, L2).
concat([H1|T1], L2, [H1|Res]) :- concat(T1, L2, Res).


% 3. sum of alternating elements of a list.
% altSum(List, Result).
altSum([], 0).
altSum([E|R], Res) :- altSum(R, ResBkt), Res is E - ResBkt.


% 4. remove element from list.
% remove(Element, InitialList, ResultingList).
remove(_, [], []).
remove(E, [E|R], L) :- remove(E, R, L).
remove(E, [F|R], [F|L]) :- dif(E, F), remove(E, R, L).


% 5. count element frequency.
% count(Element, List, Frequency).
count(_, [], 0).
count(X, [X|R], Res) :- count(X, R, ResBkt), Res is 1 + ResBkt.
count(X, [Y|R], Res) :- dif(X, Y), count(X, R, ResBkt), Res is ResBkt.


% 6. insert element in list at given position
% insertAtPos(Element, Position, InitialList, ResultingList)
insertAtPos(E, 0, [], [E]).
insertAtPos(E, 0, L, [E|L]).
insertAtPos(E, P, [H|T], Res) :- PNew is P - 1, insertAtPos(E, PNew, T, ResBkt), Res = [H|ResBkt].


% 7. mergesort.
% mergesort(List1, List2, ResultingList).
mergesort(L1, [], L1).
mergesort([], L2, L2).
mergesort([E1|R1], [E2|R2], Res) :- E1 =< E2, mergesort(R1, [E2|R2], ResBkt), Res = [E1|ResBkt].
mergesort([E1|R1], [E2|R2], Res) :- E1 > E2, mergesort([E1|R1], R2, ResBkt), Res = [E2|ResBkt].


% 8. reverse list 
reverseList([], []).
reverseList([X], [X]).
reverseList([E|R], Res) :- reverseList(R, ResBkt), append(ResBkt, [E], Res).
