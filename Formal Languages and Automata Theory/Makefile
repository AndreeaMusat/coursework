.PHONY: clean

build: flex tema

flex: lexer.lex
	flex lexer.lex

tema: lex.yy.c grammar.cpp
	g++ -o tema lex.yy.c -lfl

run: 
	./tema $(arg)

clean:
	rm tema lex.yy.c
