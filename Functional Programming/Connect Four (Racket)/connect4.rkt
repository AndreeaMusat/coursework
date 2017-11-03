#lang racket

(require racket/include)
(include "connect4-test.rkt")

(define RED 1)
(define YELLOW 2)
(define EMPTY 0)
(define INFINITY 99999)

(define init-state
  (λ (height width player)
    (cons player (init-board height width))))

; reprezint tabla de joc ca '(dim-coloana lista-coloane)
(define init-board
  (λ (height width)
    (cons height (build-list width (const (build-list height (const EMPTY)))))))

(cdr (init-board 4 5))

(define check-empty-list
  (λ (L)
    (if (empty? L)
        #t
        (if (not (equal? (car L) EMPTY))
            #f
            (check-empty-list (cdr L))))))

(define check-empty
  (λ (L)
    (if (empty? L)
        #t
        (and (check-empty-list (car L))
             (check-empty (cdr L))))))

(define is-empty-board?
  (λ (board)
    (check-empty (cdr board))))

(define get-height
  (λ (board)
    (car board)))

; numara cate coloane are lista cdr(board)
(define get-width
  (λ (board)
    (length (cdr board))))

; returneaza al n-lea element din lista l
(define getNth                     
   (lambda (n list)                   
      (cond ((null? list) '())             
            ((= n 0) (car list))              
            (else (getNth (- n 1) (cdr list))))))

; returneaza elementul din lista nr list-index
; de pe pozitia pos-index
(define get-disc
  (λ (board position)
    (let ((pos-index (cdr position))
          (list-index (car position)))
      (getNth pos-index (getNth list-index (cdr board))))))

; un state = lista player board
(define get-player
  (λ (state)
    (car state)))

; board = a doua componenta din state
(define get-board
  (λ (state)
    (cdr state)))

(define state-test
  (list YELLOW
        6
        (list EMPTY EMPTY EMPTY EMPTY EMPTY EMPTY)
        (list EMPTY EMPTY EMPTY EMPTY EMPTY EMPTY)
        (list RED YELLOW RED RED YELLOW RED)
        (list YELLOW RED RED YELLOW RED EMPTY)
        (list RED EMPTY EMPTY EMPTY EMPTY EMPTY)
        (list YELLOW YELLOW RED EMPTY EMPTY EMPTY)
        (list YELLOW YELLOW EMPTY EMPTY EMPTY EMPTY)))


;; Task 1 a) - Determinarea acțiunilor posibile
; functie care verifica daca intr-o lista exista cel putin
; un element EMPTY
(define has-empty?
  (λ (L)
    (if (empty? L)
        #f
        (if (equal? (car L) EMPTY)
            #t
            (has-empty? (cdr L))))))

; functie care adauga intr-o lista indecsii tuturor coloanelor
; care au cel putin un element EMPTY
; L e o lista de liste
(define get-available-actions-aux
  (λ (L pos result)
    ; daca lista nu mai contine nicio lista => returnez rezultatul de pana acum
    (if (null? L)
        result
        ; daca prima lista din L contine o pozitie EMPTY, atunci
        ; adaug pozitia respectiva la rezultat (cons result pos) si apelez
        ; recursiv functia pentru a gasi pozitiile libere din restul listei
        (if (has-empty? (car L))
            (get-available-actions-aux (cdr L) (+ 1 pos) (append result (list pos)))
            (get-available-actions-aux (cdr L) (+ 1 pos) result)))))
    
(define get-available-actions
  (λ (board)
    ; apelez functia auxiliara de gasire a coloanelor cu
    ; pozitii libere - incepand cu pozitia 0 si adaugand
    ; rezultatele intr-o lista empty
    (get-available-actions-aux (cdr board) 0 empty)))

; functie care schimba valoarea primului EMPTY in player
; (returneaza o noua lista)
(define replace
  (λ (player L)
    (cond
      ; daca lista e nula, nu e nimic de inlocuit => returnez lista nula
      ((null? L) '())
      ; daca primul element din lista e EMPTY => returnez o lista formata
      ; din noul player la care concatenez restul listei nemodificat
      ((equal? (car L) EMPTY) (cons player (cdr L)))
      ; altfel las primul element nemodificat si apelez recursiv functia
      ; pe restul listei
      (else (cons (car L) (replace player (cdr L)))))))

(replace RED (list RED YELLOW YELLOW EMPTY EMPTY))

(define apply-action-aux
  (λ (board list-index current-index player result)
    (cond
      ; daca prima lista din board (= lista nr current-list din board-ul
      ; initial) este chiar cea cu nr list-index =>
      ; appendez la rezultat: 1. linia curenta in care inlocuiesc prima
      ; aparitie a lui EMPTY cu jucatorul curent
      ; 2. restul listei (cdr board), neschimbat
      ((equal? list-index current-index)
       (append result (list (replace player (car board))) (apply list (cdr board))))
      ; daca prima lista din board are index mai mic decat list-index,
      ; atunci appendez la rezultat lista curenta nemodificata si apelez
      ; functia recursiv pe restul listei, avand grija sa incrementez current-index
      ((< current-index list-index)
       (apply-action-aux (cdr board)
                         list-index
                         (+ 1 current-index)
                         player
                         (append result (list (car board))))))))

;; Task 1 b) - Aplicarea unei acțiuni
; se adauga un disc pe coloana nr action
; state contine: (player board) =>
; in lista nr action din cdr(board) trebuie ca ultimul
; element EMPTY sa fie inlocuit cu player
(define apply-action
  (λ (state action)
    (let* ((current-player (get-player state))
           (current-board (cdr (get-board state)))    ; get board intoarce si capacitatea unei liste
           (next-board (apply-action-aux current-board
                                         action
                                         0
                                         current-player
                                         empty)))
      (if (equal? current-player RED)
          (cons YELLOW (cons (car (get-board state)) next-board))
          (cons RED (cons (car (get-board state)) next-board))))))

(define apply-actions
  (λ (state actions)
    ; daca nu mai sunt actiuni de facut, returnez starea curenta
    (if (empty? actions)
        state
        ; altfel apelez recursiv apply-actions pe starea pe care o obtin
        ; dupa ce aplic prima actiune
        (apply-actions (apply-action state (car actions)) (cdr actions)))))

;; Task 1 c) - Verificarea stării finale

; functie care verifica daca mai exista pozitii EMPTY in board
(define is-any-empty?
  (λ (state)
    (let ((actions (get-available-actions (get-board state))))
      (if (empty? actions)
          #t
          #f))))

; functie care grupeaza elementele egale dintr-o lista in alte liste in care
; sunt doar elemente de acelasi fel
; eg: (pack '(a a a a b c c a a d e e e e)) -> '((a a a a) (b) (c c) (a a) (d) (e e e e))
; sursa functie: http://community.schemewiki.org/?S-99-09
(define pack 
   (lambda (xs) 
     (if (null? xs) '() 
       (let loop ((rest (cdr xs)) 
                  (pkg (list (car xs)))) 
         (cond ((null? rest) 
                (list pkg)) 
               ((eq? (car pkg) (car rest)) 
                (loop (cdr rest) (cons (car rest) pkg))) 
               (else 
                 (cons pkg (loop (cdr rest) (list (car rest))))))))))

; verifica daca in lista L exista cel putin 4 elemente consecutive care
; sa aiba aceeasi valoare
(define check-victory-column
  (λ (L)
    ; mapez lista la o serie de perechi (lungime . valoare), unde
    ; lungime = lungimea unei secvente de elemente consecutive din lista
    ; initiala care au aceeasi valoare
    (let ((freq (map (λ (l) (cons (length l) (car l))) (pack L))))
      (let iter ((freq freq))
        ; daca am verificat toate elementele si nu am gasit victorie => return #f
        (if (null? freq)
            #f
            ; daca am gasit un element non EMPTY cu frecventa >= 4 => returnez valoarea 
            (if (and (>= (car (car freq)) 4)
                     (not (equal? (cdr (car freq)) EMPTY)))
                (cdr (car freq))
                ; altfel continui sa verific daca in perechile urmatoare exista
                ; un element cu frecventa >= 4
                (iter (cdr freq))))))))

; se verifica o victorie pe verticala in state-ul curent
(define check-victory-vertical
  (λ (state)
    (let ((board (cdr (get-board state))))
      (if (null? board)
          #f
          (let iter ((board board))
            ; daca board-ul curent e gol => nu am gasit nicio victorie, returnez #f
            (if (empty? board)
                #f
                ; altfel veritic victoria pe coloana curenta
                ; si in cazul in care nu e #f, returnez valoarea
                (let ((crt-col-victory (check-victory-column (car board))))
                  (if (not (equal? #f crt-col-victory))
                      crt-col-victory
                      ; daca pe coloana curenta nu e victorie, verific la urmatoarele
                      (iter (cdr board))))))))))

(define (transpose l)
  (apply map list l))

; functie care verifica daca exista o victorie pe orizontala
; se face transpusa board-ului si se reduce la check-victory-vertical
(define check-victory-horizontal
  (λ (state)
    (let* ((new-columns (transpose (cdr (get-board state))))
           (new-state (cons (car state) (cons (cadr state) new-columns))))
      (check-victory-vertical new-state))))

; functie care adauga padding (de dimensiune beg la inceput si end la final)
; unei liste L
(define add-padding
  (λ (L beg end)
    (append (build-list (max 0 beg) (const INFINITY))
            L
            (build-list (max 0 end) (const INFINITY)))))

; functie care creeaza diagonalele unei matrice
; adaugand padding
; de exemplu:
; pentru '((1 2 3) (a b c))
; se va obtine '((1 2 3 99999 99999) (99999 a b c 99999)) si
; => '(1), '(2 a), '(3 c) vor fi diagonale valide (\)
; si '((99999 99999 1 2 3) (99999 a b c 99999)) =>
; '(a), '(1 b), '(2 c), '(3) sunt diagonale valide
(define create-diag-aux
  (λ (L crt-index length-index result1 result2)
    (if (null? L)
        (cons result1 result2)
        (let ((crt-index-compl (- length-index crt-index)))
          (create-diag-aux (cdr L)
                            (+ 1 crt-index)
                            length-index
                            (append result1
                                    (list (add-padding (car L)
                                                       crt-index
                                                       crt-index-compl)))
                            (append result2
                                    (list (add-padding (car L)
                                                       crt-index-compl
                                                       crt-index))))))))

(define create-diag
  (λ (L)
    (create-diag-aux L 0 (length L) empty empty)))

(create-diag '((1 2 3) (a b c)))
; functie care primeste o lista de diagonale si verfica daca vreuna contine
; o victorie
(define check-victory-diagonal-aux
  (λ (L)
    ; mapez fiecare diagonala cu rezultatul intors de check-victory
    (let ((mapped-victory (map check-victory-column L)))
      (cond
        ; daca exista o valoare 1 => 1 a castigat etc
        ((member 1 mapped-victory) 1)
        ((member 2 mapped-victory) 2)
        (else #f)))))

(define get-diag-list
  (λ (L)
    (map (λ (l) (remove* (list INFINITY) l))
         (transpose L))))

(define check-victory-diagonal
  (λ (state)
    (let* ((board (cdr (get-board state)))
           ; diags = pereche de liste: diagonale cu orientare / si diagonale cu orientare \
           (diags (create-diag board))
           (diag1-list (get-diag-list (car diags)))
           (diag2-list (get-diag-list (cdr diags)))
           (victory1 (check-victory-diagonal-aux diag1-list))
           (victory2 (check-victory-diagonal-aux diag2-list)))
      (if (not (equal? #f victory1))
          victory1
          (if (not (equal? #f victory2))
              victory2
              #f)))))
                     
; functie care verifica daca jocul s-a terminat
; se returneaza: 3 daca nu mai exista pozitii EMPTY
;                1 sau 2 daca a castigat RED/YELLOW
;               #f daca nu e finala
(define is-game-over?
  (λ (state)
    (cond
      ((is-any-empty? state) 3)
      (else
       (let ((vertical-victory (check-victory-vertical state))
             (horizontal-victory (check-victory-horizontal state))
             (diagonal-victory (check-victory-diagonal state)))
         (cond
           ; daca s-a descoperit o victorie pe verticala => returnez codul victoriei
           ((not (equal? #f vertical-victory)) vertical-victory)
           ; daca s-a descoperit o victorie pe orizontala => returnez codul victoriei
           ((not (equal? #f horizontal-victory)) horizontal-victory)
           ; daca s-a descoperit o victorie pe diagonala => returnez codul victoriei
           ((not (equal? #f diagonal-victory)) diagonal-victory)
           ; altfel nu s-a descoperit nicio victorie => false
           (else #f)))))))

;; Task 2 - Euristică simplă
(define select-random-action
  (λ (state rand-gen)
   ; actions = toate mutarile posibile acum
   (let* ((actions (get-available-actions state))
          ; un numar random (intre 0 si 1)
          (rand-no (random rand-gen))
          ; o pozitie random bazata pe numarul random generat anterior
          (rand-pos (floor (* rand-no (length state)))))
     (getNth rand-pos actions))))

; functie care intoarce indexul unui element intr-o lista
; sursa: http://stackoverflow.com/questions/15871042/how-do-i-find-the-index-of-an-element-in-a-list-in-racket
(define (index-of lst ele)
  (let loop ((lst lst)
             (idx 0))
    (cond ((null? lst) #f)
          ((equal? (car lst) ele) idx)
          (else (loop (rest lst) (add1 idx))))))

; intoarce oponentul unui jucator dat ca parametru
(define (get-opponent player)
  (cond
    ((equal? player RED) YELLOW)
    ((equal? player YELLOW) RED)))

; daca exista actiuni prin care jucatorul curent castiga => le returnez
; altfel verifica daca exista actiuni prin care impiedica victoria adversarului
; altfel orice
(define get-action
  (λ (state)
    (let* ((crt-player (get-player state))
           (opponent (get-opponent crt-player))
           (board (get-board state))
           ; actions = toate mutarile valabile
           (actions (get-available-actions board))
           ; mapare -> pentru fiecare mutare posibila a jucatorului curent am codul victoriei in cazul respectiv
           (game-over (map (λ (action) (is-game-over? (apply-action state action))) actions))
           ; state-ul curent daca oponentul ar trebui sa faca mutarea curenta
           (opp-state (cons opponent board))
           ; maparea -> pentru fiecare mutare posibila a oponentului mapez la codul victoriei dupa mutare
           (game-over-opp (map (λ (action) (is-game-over? (apply-action opp-state action))) actions)))
      (cond
        ; daca exista o mutare prin care castiga jucatorul curent, o returnez
        ((member crt-player game-over) (getNth (index-of game-over crt-player) actions))
        ; daca exitsa mutare prin care castiga adversarul, o returnez
        ((member opponent game-over-opp) (getNth (index-of game-over-opp opponent) actions))
        ; altfel returnez mutare random
        (else (select-random-action state current-pseudo-random-generator))))))
               

(define AI #f) ;Trebuie modificat în #t după ce se implementează play-game

;(define play-game-aux
;  (λ (state strategy1 strategy2 result)
;    (let* ((crt-player (get-player state))
;           (game-over (is-game-over? state))
;           (func (car strategy1))
;           (arg (cdr strategy1))
;           (action (func state arg)))
;      (if (>= game-over 1)
;          (cons result game-over)
;          (play-game-aux (apply-action state action) strategy2 strategy1 (append result action))))))
;
;(define play-game
;  (λ (state strategy1 strategy2)
;   (play-game-aux state strategy1 strategy2 empty)))

(define play-game
  (λ (state strategy1 strategy2)
    'your_code_here))

;; Bonus 
(define evaluate
  (λ (state)
    ;TODO
    'your-code-here))

(define negamax
  (λ (state maxDepth)
    ;TODO
    'your-code-here))
     
;; SECȚIUNE DE TESTARE - NU modificați această linie!
;; ATENȚIE! Pentru a primi punctaj pe temă, NU modificați această secțiune!
;;
;; CHECK - TASK 0 - NU modificați această linie!
;; ATENȚIE! NU modificați această secțiune
(Task 0 : 20 puncte) ;;check-exp
(check-exp-part 'is-empty-board?1 .02 (is-empty-board? (init-board 7 7)) #t)
(check-exp-part 'is-empty-board?2 .02 (is-empty-board? (get-board state-test)) #f)
(check-exp-part 'is-empty-board?3 .02 (is-empty-board? (get-board (init-state 7 8 RED))) #t)
(check-exp-part 'get-height1 .02 (get-height (get-board (init-state 7 8 YELLOW))) 7)
(check-exp-part 'get-height2 .02 (get-height (get-board state-test)) 6)
(check-exp-part 'get-height3 .02 (get-height (init-board 10 14)) 10)
(check-exp-part 'get-width1 .02 (get-width (get-board (init-state 7 8 YELLOW))) 8)
(check-exp-part 'get-width2 .02 (get-width (get-board state-test)) 7)
(check-exp-part 'get-width3 .02 (get-width (init-board 10 14)) 14)
(check-exp-part 'get-width4 .01 (get-width (init-board 20 20)) 20)
(check-exp-part 'get-player1 .02 (get-player state-test) YELLOW)
(check-exp-part 'get-player2 .02 (get-player (init-state 15 7 RED)) RED)
(check-exp-part 'get-player3 .02 (get-player (init-state 10 8 YELLOW)) YELLOW)
(check-exp-part 'get-disc1 .05 (get-disc (get-board (init-state 10 8 YELLOW)) (cons 1 2)) EMPTY)
(check-exp-part 'get-disc2 .05 (get-disc (get-board state-test) (cons 1 2)) EMPTY)
(check-exp-part 'get-disc3 .05 (get-disc (get-board state-test) (cons 5 0)) YELLOW)
(check-exp-part 'get-disc4 .05 (get-disc (get-board state-test) (cons 5 1)) YELLOW)
(check-exp-part 'get-disc5 .05 (get-disc (get-board state-test) (cons 5 2)) RED)
(check-exp-part 'get-disc6 .05 (get-disc (get-board state-test) (cons 5 3)) EMPTY)
(check-exp-part 'get-disc7 .05 (get-disc (get-board state-test) (cons 2 3)) RED)
(check-exp-part 'get-disc8 .05 (get-disc (get-board state-test) (cons 2 5)) RED)
(check-exp-part 'get-disc9 .05 (get-disc (get-board state-test) (cons 3 0)) YELLOW)
(check-exp-part 'get-disc10 .05 (get-disc (get-board state-test) (cons 3 3)) YELLOW)
(check-exp-part 'get-disc11 .05 (get-disc (get-board state-test) (cons 6 0)) YELLOW)
(check-exp-part 'get-disc12 .05 (get-disc (get-board state-test) (cons 6 1)) YELLOW)
(check-exp-part 'get-disc13 .05 (get-disc (get-board state-test) (cons 6 5)) EMPTY)
(check-exp-part 'get-disc14 .05 (get-disc (get-board state-test) (cons 0 0)) EMPTY)
(check-exp-part 'get-disc15 .05 (get-disc (get-board state-test) (cons 6 5)) EMPTY)
;; SFÂRȘIT CHECK - TASK 0 - NU modificați această linie!
;;
;; CHECK - Task1 - NU modificați această linie!
;; ATENȚIE! NU modificați această secțiune!
(Task 1 : 50 puncte) ;;check-exp
(check-exp-part 'get-available-actions1 .04 (get-available-actions (get-board state-test)) '(0 1 3 4 5 6))
(check-exp-part 'get-available-actions2 .04 (get-available-actions (init-board 7 9)) '(0 1 2 3 4 5 6 7 8))
(check-exp-part 'get-available-actions3 .04 (get-available-actions (get-board (init-state 10 8 YELLOW))) '(0 1 2 3 4 5 6 7))
(check-exp-part 'get-available-actions4 .04 (get-available-actions (get-board (apply-action state-test 3))) '(0 1 4 5 6))
(check-exp-part 'get-available-actions5 .04 (get-available-actions (get-board (apply-actions state-test '(3 5 5 5)))) '(0 1 4 6))
(check-exp-part 'apply-action1 .02 (get-disc (get-board (apply-action state-test 3)) (cons 3 5)) YELLOW)
(check-exp-part 'apply-action2 .02 (get-player (apply-action state-test 3)) RED)
(check-exp-part 'apply-action3 .02 (get-player (apply-action (init-state 7 7 YELLOW) 1)) RED)
(check-exp-part 'apply-action4 .02 (get-disc (get-board (apply-action (init-state 6 6 RED) 1)) (cons 1 0)) RED)
(check-exp-part 'apply-action5 .02 (get-disc (get-board (apply-action (init-state 4 6 YELLOW) 2)) (cons 2 0)) YELLOW)
(check-exp-part 'apply-actions1 .02 (get-player (apply-actions (init-state 7 6 YELLOW) '(1 0 2 1 1 3 4 1 2 3))) YELLOW)
(check-exp-part 'apply-actions2 .02 (get-disc (get-board (apply-actions (init-state 6 6 RED) '(0 1 1 0 1 1 0 2 3))) (cons 0 2)) RED)
(check-exp-part 'apply-actions3 .02 (get-available-actions (get-board (apply-actions (init-state 6 6 RED) '(0 1 1 0 1 1 0 2 3 1 1)))) '(0 2 3 4 5))
(check-exp-part 'apply-actions4 .02 (get-available-actions (get-board (apply-actions (init-state 4 4 RED) '(1 1 1 1 0 0 0 0 2 2 2 2 3 3)))) '(3))
(check-exp-part 'apply-actions5 .02 (get-available-actions (get-board (apply-actions state-test '(1 1 1 1 1 1 0 0 0 0 0 0)))) '(3 4 5 6))
(check-exp-part 'apply-actions6 .02 (get-available-actions (get-board (apply-actions (init-state 4 4 RED) '(2 0 0 0 1 1 3 0 2 2 1 1 3 3 3 2)))) '())
(check-exp-part 'apply-actions7 .02 (get-available-actions (get-board (apply-actions (init-state 7 9 YELLOW) '(5 5 8 5 5 8 8 0 0 4 1 5 5 6 1 1 7 8 2 3 1 5 3 6 1 0 3 1 1 0 4 3 2)))) '(0 2 3 4 6 7 8))
(check-exp-part 'apply-actions8 .02 (get-available-actions (get-board (apply-actions (init-state 12 12 RED) '(9 6 8 10 3 1 1 3 7 5 11 11 7 3 11 0 5 6 7 9 5 3 0 10 5 10 10 6 1 7 0 3)))) '(0 1 2 3 4 5 6 7 8 9 10 11))
(check-exp-part 'apply-actions9 .02 (get-available-actions (get-board (apply-actions (init-state 15 15 YELLOW) '(8 10 0 13 9 2 9 6 1 5 14 6 3 3 11 5 13 7 13 13 3 13 10 8 9 11 1 12 12 6 4 5 2 12)))) '(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14))
(check-exp-part 'apply-actions10 .02 (get-available-actions (get-board (apply-actions (init-state 8 15 RED) '(6 1 3 3 10 12 14 1 8 3 9 10 3 11 3 9 7)))) '(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14))
(check-exp-part 'is-game-over?1 .01 (is-game-over? (apply-actions (init-state 4 4 RED) '(1 1 1 1 0 0 0 0 2 2 2 2 3))) RED)
(check-exp-part 'is-game-over?2 .01 (is-game-over? (apply-actions (init-state 5 7 RED) '(0 3 1 3 2 3 4 4 5 0 1 5 0 6 6 2))) YELLOW)
(check-exp-part 'is-game-over?3 .01 (is-game-over? (apply-actions (init-state 5 6 YELLOW) '(0 1 2 3 4 5 5 4 3 2 1 0 0 1 3 2 3 2 0 3))) RED)
(check-exp-part 'is-game-over?4 .01 (is-game-over? (apply-actions (init-state 4 4 RED) '(1 1 1 1 0 0 0 0 2 2 2 2))) #f)
(check-exp-part 'is-game-over?5 .01 (is-game-over? (apply-actions (init-state 6 6 YELLOW) '(0 5 0 5 0 3 0))) YELLOW)
(check-exp-part 'is-game-over?6 .01 (is-game-over? state-test) #f)
(check-exp-part 'is-game-over?7 .02 (is-game-over? (apply-actions (init-state 4 4 RED) '(2 0 0 0 1 1 3 0 2 2 1 1 3 3 3 2))) 3)
(check-exp-part 'is-game-over?8 .02 (is-game-over? (apply-actions (init-state 8 15 RED) '(6 1 3 3 10 12 14 1 8 3 9 10 3 11 3 9 7))) RED)
(check-exp-part 'is-game-over?9 .02 (is-game-over? (apply-actions (init-state 8 15 YELLOW) '(6 8 5 2 1 4 9 7 12 9 12 9 8 3 3 10 6 7 11 6 12 13 9 6 0 6 10 7 1 10 7 12 13 14 8 11 7 7 7 5 7 9 2 11 1 3 11 12 3 12 11 9 11 1 8 9 12 14 5 3 2))) YELLOW)
(check-exp-part 'is-game-over?10 .02 (is-game-over? (apply-actions (init-state 8 8 RED) '(2 0 0 1 7 0 1 4 7 2 1 3 6 7 7 6 3 3 3 7 7 2 0 4 4 3 7 4))) YELLOW)
(check-exp-part 'is-game-over?11 .02 (is-game-over? (apply-actions (init-state 4 20 RED) '(16 13 8 13 17 14 5 0 15 13 18))) RED)
(check-exp-part 'is-game-over?12 .02 (is-game-over? (apply-actions (init-state 7 7 RED) '(4 4 0 1 1 4 1 1 1 5 3 1 4 6 4 2 0 5 6 3 6 5 0 6 3 1 5 3))) YELLOW)
(check-exp-part 'is-game-over?13 .02 (is-game-over? (apply-actions (init-state 5 8 RED) '(5 1 0 0 1 6 7 4 7 2 4 2 3 3 4 4 6 2 2 0 1 6 4 3))) YELLOW)
(check-exp-part 'is-game-over?14 .02 (is-game-over? (apply-actions (init-state 4 8 RED) '(0 0 0 0 1 1 1 1 2 3 2 2 2 3 4 3 3 4 4 4 5 5 5 5 7 6 6 6 6 7 7 7))) 3)
(check-exp-part 'is-game-over?15 .02 (is-game-over? (apply-actions (init-state 4 8 RED) '(1 0 5 3 7 0 0 1 6 0 7 1 7 6 5 2))) #f)
(check-exp-part 'is-game-over?16 .02 (is-game-over? (apply-actions (init-state 9 4 YELLOW) '(0 2 1 1 3 3 1 0 2 1 2 2 3 3 1 0 2 3 2 3 0))) YELLOW)
(check-exp-part 'is-game-over?17 .02 (is-game-over? (apply-actions (init-state 9 4 RED) '(1 1 1 1 3 0 0 2 1 1 2 2 0 2 1 1 3 2))) #f)
(check-exp-part 'is-game-over?18 .02 (is-game-over? (apply-actions (init-state 5 5 RED) '(4 3 2 4 3 2 3 2 0 1 1 0 4 2 3 4 2 1 4 0 1 3))) 2)
(check-exp-part 'is-game-over?19 .02 (is-game-over? (apply-actions (init-state 7 4 RED) '(2 0 0 2 1 3 1 0 3 0 2 0 0 0 2 1))) 2)
(check-exp-part 'is-game-over?20 .02 (is-game-over? (apply-actions (init-state 7 9 YELLOW) '(1 6 5 2 0 3 2 2 6 4 3 1 1 0 1 5 8 5 5 7 2 8 2 1 1 2 5 0 5 6 6 8 4 7 2 0 1 8 7 7))) 1)
(check-exp-part 'is-game-over?21 .02 (is-game-over? (apply-actions (init-state 5 9 YELLOW) '(8 0 7 6 6 0 1 5 6 0 7 5 4 8 5 6 0 0 5))) 2)
(check-exp-part 'is-game-over?22 .02 (is-game-over? (apply-actions (init-state 10 4 YELLOW) '(2 1 2 0 3 1 3 0 0 3 0 2 1))) 2)
(check-exp-part 'is-game-over?23 .02 (is-game-over? (apply-actions (init-state 10 6 RED) '(0 0 4 1 2 5 0 0 1 4 0 1 1 3 2 0 4 1 2 2 0 1 1 5 1 1 1 5 2 2 5 5 3))) 1)
(check-exp-part 'is-game-over?24 .02 (is-game-over? (apply-actions (init-state 10 4 YELLOW) '(2 1 2 0 3 1 3 0 0 3 0 2 1))) 2)
(check-exp-part 'is-game-over?25 .02 (is-game-over? (apply-actions (init-state 10 7 YELLOW) '(3 1 3 1 4 5 2 0 1 0 2 0 2 6 4 2 1))) 2)
(check-exp-part 'is-game-over?26 .02 (is-game-over? (apply-actions (init-state 10 10 YELLOW) '(2 9 3 5 7 2 6 1 0 4 8 7 2 5 0 9 5 5 7 1 6 7 7 6))) 1)
(check-exp-part 'is-game-over?27 .02  (is-game-over? (apply-actions (init-state 6 4 RED) '(0 1 2 3 3 2 1 0 0 1 2 3 0 1 3))) 1)
(check-exp-part 'is-game-over?28 .02 (is-game-over? (apply-actions (init-state 5 6 RED) '(0 1 2 3 4 5 5 4 2 3 1 0 0 1 3 2 3 4 4 5 0 5 5))) RED)
;; SFÂRȘIT CHECK - TASK 1 - NU modificați această linie!
;;
;; CHECK - Task2 - NU modificați această linie!
;; ATENȚIE! NU modificați această secțiune!
(Task 2 : 30 puncte) ;;check-exp
(define FUNCTIONS (list is-game-over? play-game get-available-actions apply-actions)) ;;check-exp
(check-in-part 'get-action1 .1 (get-action (apply-actions (init-state 9 4 YELLOW) '(0 0 3 3 3 2 2 1 2 2 3 1 0 1 0))) '(1 3))
(check-in-part 'get-action2 .1 (get-action (apply-actions (init-state 7 7 RED) '(1 4 2 4 6 2 1 4 1 0 5 3 6 0 5 1 5 0 4 2 1 5))) '(0 3))
(check-exp-part 'get-action3 .1 (get-action (apply-actions (init-state 10 6 YELLOW) '(3 4 3 3 4 5 4 2 3 2 3 3 2 4 2 3 3 2 4 4 0 0 3 4 1 0 3 1 0 1 5 2))) 1)
(check-exp-part 'get-action4 .05 (get-action (apply-actions (init-state 4 4 YELLOW) '(1 0 1 1 0 3 0 0 3 2 3 3))) 2)
(check-exp-part 'get-action5 .05 (get-action (apply-actions (init-state 4 4 RED) '(0 3 2 3 3 1 1 2 2))) 3)
(check-exp-part 'get-action6 .05 (get-action (apply-actions (init-state 8 8 RED) '(3 0 2 1 6 6 5 1))) 4)
(check-exp-part 'get-action7 .1 (get-action (apply-actions (init-state 10 5 YELLOW) '(1 2 4 1 3 0 3 2 2 1 2 1 2))) 1)
(check-exp-part 'get-action8 .1 (get-action (apply-actions (init-state 12 12 YELLOW) '(6 3 0 9 4 2 10 7 1 7 0 0 9 2 0 8 2 8 8 10 10 10 5 2 3 11 4 4 4 8 3 2 2 11 11 8 8))) 9)
(check-in-part 'get-action9 .1 (get-action (apply-actions (init-state 20 8 RED) '(3 2 2 1 2 7 2 5 0 6 1 5 0 5))) '(2 3))
(check-in-part 'get-action10 .1 (get-action (apply-actions (init-state 10 10 YELLOW) '(0 4 0 5 0 6 1 7 1 8 1 9 2 9 2 8 2))) '(0 1 2 3 4 5 6 7 8 9))
(check-exp-part 'play-game1 .025 (check-game AI (init-state 8 9 RED) (cons select-random-action (current-pseudo-random-generator)) (cons  select-random-action (current-pseudo-random-generator)) FUNCTIONS 1) #t)
(check-exp-part 'play-game2 .025 (check-game AI (init-state 9 8 YELLOW) (cons simple-strategy 'None) (cons  simple-strategy 'None) FUNCTIONS 1) #t) 
(check-exp-part 'play-game3 .025 (check-play-game AI (init-state 7 7 YELLOW) (cons simple-strategy 'None) (cons  select-random-action (current-pseudo-random-generator)) FUNCTIONS 4 YELLOW #f) #t) 
(check-exp-part 'play-game4 .025 (check-game AI state-test (cons select-random-action (current-pseudo-random-generator)) (cons  select-random-action (current-pseudo-random-generator)) FUNCTIONS 1) #t) 
(check-exp-part 'play-game5 .025 (check-play-game AI (init-state 10 5 YELLOW) (cons simple-strategy 'None) (cons  select-random-action (current-pseudo-random-generator)) FUNCTIONS 4 YELLOW #f) #t) 
(check-exp-part 'play-game6 .025 (check-play-game AI (init-state 10 10 YELLOW) (cons simple-strategy 'None) (cons  select-random-action (current-pseudo-random-generator)) FUNCTIONS 4 YELLOW #f) #t) 
;; SFÂRȘIT CHECK - TASK 2 - NU modificați această linie!
;;
;; CHECK - BONUS - NU modificați această linie!
;; ATENȚIE! NU modificați această secțiune
(Bonus 3 : 20 puncte BONUS) ;;check-exp
(check-exp-part 'bonus1 .1 (check-play-game AI state-test (cons negamax 1) (cons negamax 3) FUNCTIONS 4 RED #t) #t)
(check-exp-part 'bonus2 .1 (check-play-game AI state-test (cons select-random-action (current-pseudo-random-generator)) (cons negamax 4) FUNCTIONS 4 RED #t) #t)
(check-exp-part 'bonus3 .1 (check-play-game AI (apply-actions (init-state 4 6 RED) '(1 0 1 1 0 3)) (cons select-random-action (current-pseudo-random-generator)) (cons negamax 5) FUNCTIONS 6 YELLOW #t) #t)
(check-exp-part 'bonus4 .1 (check-play-game AI (init-state 7 7 YELLOW) (cons select-random-action (current-pseudo-random-generator)) (cons negamax 3) FUNCTIONS 6 RED #t) #t)
(check-exp-part 'bonus5 .1 (check-play-game AI (apply-actions (init-state 9 6 YELLOW) '(1 2 0 3 1 0 2 4 5 0)) (cons select-random-action (current-pseudo-random-generator)) (cons negamax 3) FUNCTIONS 6 RED #t) #t)
(check-exp-part 'bonus6 .1 (check-play-game AI (init-state 8 8 RED) (cons negamax 1) (cons negamax 3) FUNCTIONS 6 YELLOW #t) #t)
(check-exp-part 'bonus7 .1 (check-play-game AI (init-state 4 6 RED) (cons negamax 1) (cons negamax 5) FUNCTIONS 4 YELLOW #t) #t)
(check-exp-part 'bonus8 .1 (check-play-game AI (init-state 5 7 RED) (cons negamax 2) (cons negamax 5) FUNCTIONS 2 YELLOW #t) #t)
(check-exp-part 'bonus9 .1 (check-play-game AI (apply-actions (init-state 10 8 RED) '(1 5 2 6 7 1 0 2 6 4 0 7 7)) (cons negamax 2) (cons negamax 4) FUNCTIONS 4 YELLOW #t) #t)
(check-exp-part 'bonus10 .1 (check-play-game AI (apply-actions (init-state 10 6 RED) '(1 0 1 1 0 3)) (cons select-random-action (current-pseudo-random-generator)) (cons negamax 3) FUNCTIONS 4 YELLOW #t) #t)
;; SFÂRȘIT CHECK - BONUS - NU modificați această linie!
;; SFÂRȘIT SECȚIUNE DE TESTARE
(sumar)
