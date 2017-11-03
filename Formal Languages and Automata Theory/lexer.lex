%{
	#include <iostream>
	#include <cstdio>
	#include "grammar.cpp"

	using namespace std;
		
	bool found_v = false;
	bool found_e = false;
	bool found_r = false;
	bool found_s = false;
	
	grammar g;
%}
	
special        "-"|"="|"["|"]"|";"|"\\"|"."|"/"|"~"|"!"|"@"|"#"|"$"|"%"|"^"|"&"|"*"|"_"|"+"|":"|"|"|"<"|">"|"?"|"'"|"`"|"\""

space          [" "\n\t\r]
digit          [0-9]
lo_let         [a-d]|[f-z]
up_let         [A-Z]
symbol         {special}|{digit}|{lo_let}|{up_let}

terminal       {lo_let}|{digit}|{special}
nonterminal    {up_let}
replacement    "e"|{symbol}+
rule 	       {space}*"("{space}*{nonterminal}{space}*","{space}*{replacement}{space}*")"{space}*

comma_symbol   {space}*","{space}*{symbol}{space}*
comma_terminal {space}*","{space}*{terminal}{space}*
comma_rule     {space}*","{space}*{rule}{space}*
     
empty_set        {space}*"{"{space}*"}"{space}*","

/* regular expressions for the components of the grammar 
<CFG> ::= ( <(non)terminals> , <alphabet> , <production rules> , <startsymbol> )
	          v           |    e       |        r           |    s   

v = <(non)terminals> ::= { <(non)terminal> ( , <(non)terminal> )* }
e = <alphabet> ::= { ( <terminal> ( , <terminal> )* )? }
r = <production rules> ::= { ( <production rule> ( , <production rule> )* )?}
s = <start symbol> ::= <upper-case letter> */

v              {space}*"("{space}*"{"{space}*{symbol}{space}*{comma_symbol}*{space}*"}"{space}*","
e	                  {space}*"{"{space}*{terminal}{space}*{comma_terminal}*{space}*"}"{space}*","
r	                  {space}*"{"{space}*{rule}{space}*{comma_rule}*{space}*"}"{space}*","        
s                         {space}*{nonterminal}{space}*")"{space}*

%%

{v} {
	string text = remove_whitespace(string(yytext));
	g.get_v(text);	
	found_v = true;
}

{empty_set} {
	if (found_v == true && found_e == false) {
		found_e = true;
	}
	else if (found_e == true && found_r == false) {
		found_r = true;
	}

}

{r} {
	if (found_e == true && found_r == false) {
		string text = remove_whitespace(string(yytext));
		g.get_r(text);
		found_r = true;
	}

}

{e} {
	if (found_v == true && found_e == false) {
		string text = remove_whitespace(string(yytext));
		g.get_e(text);
		found_e = true;
	}
}


{s} {
	if (found_r == true && found_s == false) {
		string text = remove_whitespace(string(yytext));
		g.set_start_symbol(text[0]);
		found_s = true;
	}
}

. {
	cerr << "Syntax error\n";
	exit(0);
}

%%


int main(int argc, char **argv) {

	if (argc != 2) {
		cerr << "Argument error\n";
		return 0;
	}

	if (strcmp("--is-void", argv[1]) && 
	    strcmp("--has-e", argv[1]) &&
            strcmp("--useless-nonterminals", argv[1])) {
		cerr << "Argument error\n";
		return 0;
	}

	FILE* f = fopen("grammar", "rt");
	yyrestart(f);
	yylex();
	fclose(f);

	if (!found_v || !found_e || !found_r || !found_s) {
		cerr << "Syntax error\n";
		return 0;
	}
  
	if (g.check_semantic_errors()) {
		cerr << "Semantic error\n";
		return 0;
	}

	g.answer_query(string(argv[1]));   

	return 0;
}
