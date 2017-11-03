#include <stdio.h>
#include <vector>
#include <iostream>
#include <algorithm>
#include <cstring>

using namespace std;

bool is_space(char c) {
	return c == ' ' || c == '\n' || c == '\r' ||
	c == '\t' || c == '\v' || c == '\f';
}

string remove_whitespace(string str) {
	string new_string;
	for (size_t i = 0; i < str.size(); i++) 
		if (!is_space(str[i]))
			new_string += str[i];
		return new_string;
	}

class alphabet {
public:
	vector<char> buffer;

	alphabet() {}

	void add(char c) { 
		buffer.push_back(c); 
	}

	bool contains(char c) {

		return std::find(buffer.begin(), buffer.end(), c) != buffer.end();
	}
};

class rule {
public:
	char nonterminal;
	string replacement;

	rule() {}

	void set_nonterminal(char c) {
		nonterminal = c;
	}

	void add_char_replacement(char c) {
		replacement += c;
	}

};

class grammar {
public:
	alphabet v;
	alphabet e;
	vector<rule> rules;
	char start_symbol;
	vector<char> useless;

	grammar() {}

	void set_start_symbol(char c) {
		start_symbol = c;
		return;
	}

	void add_rule(rule rl) {
		rules.push_back(rl);
		return;
	}

	void get_v(string s) {
		// add the symbols in v
		for (size_t i = 0; i < s.size(); i++) 
			if (s[i] != ',' && s[i] != '{' && s[i] != '}' && s[i] != '(')
				v.add(s[i]);
			return;
	}

	void get_e(string s) {
		// add the symbols in e
		for (size_t i = 0; i < s.size(); i++) 
			if (s[i] != ',' && s[i] != '{' && s[i] != '}')
				e.add(s[i]);
			return;
	}

	void get_r(string r) {
		size_t i = 0;
		bool found_comma = false;
		rule crt_rule;

		while (i < r.size()) {
			// found the beginning of a new rule
			if (r[i] == '(') {
				found_comma = false;
				rule new_rule;
				crt_rule = new_rule;
				crt_rule.set_nonterminal(r[i+1]);
				i += 2;
			}
			// found the comma between the components of a rule
			else if (r[i] == ',') {
				found_comma = true;
				i += 1;
			}
			// the rule is complete now
			else if (r[i] == ')') {
				add_rule(crt_rule);
				i += 1;
			}
			// this is a replacement symbol
			else if (r[i] != ')' && r[i] != '{' && 
				     r[i] != '}' && found_comma == true) {
				crt_rule.add_char_replacement(r[i]);
				i += 1;
			}
			else i += 1;
		}
		return;
	}

	bool check_semantic_errors() {
		bool found_s = false;

		// Σ ⊂ V ?
		for (size_t i = 0; i < e.buffer.size(); i++) {
			if (!v.contains(e.buffer[i])) {
				return true;
			}
		}

		// V \ Σ is made just of nonterminals ? 
		for (size_t i = 0; i < v.buffer.size(); i++) {
			if (!e.contains(v.buffer[i])) {
				if (v.buffer[i] < 'A' || v.buffer[i] > 'Z') {
					return true;
				}
				else if (v.buffer[i] == start_symbol)
					found_s = true;
			}
		}

		// S ∈ V \ Σ ?
		if (found_s == false) {
			return true;
		}

		// ∀(A, γ) ∈ R, A ∈ V \Σ ?
		// ∀(A, γ) ∈ R, γ ∈ V ∗ ?
		for (size_t i = 0; i < rules.size(); i++) {
			if (!(v.contains(rules[i].nonterminal) && 
				!e.contains(rules[i].nonterminal))) {
				return true;
			}

			for (size_t j = 0; j < rules[i].replacement.size(); j++) {
				if (!v.contains(rules[i].replacement[j])) {
					if (rules[i].replacement[j] != 'e')
						return true;
				}
			}
		}
		return false;
	}

	void useless_nonterminals() {

		int n = 'Z' - 'A' + 1;

		// initially none of the nonterminals is marked
		bool marked[n]; 
		for (size_t i = 0; i < n; i++) 
			marked[i] = false;

		bool ok;
		do {
			ok = false;
			/* for every rule with the nonterminal not yet marked, 
			count how many characters from its replacement are generating.
			if every character is generating (either a terminal or a 
			generating nonterminal), then mark the current nonterminal 
			as generating and continue 
			*/
			for (size_t i = 0; i < rules.size(); i++) {
				if (marked[rules[i].nonterminal - 'A'] == false) {
					int cnt = 0;				
					for (size_t j = 0; j < rules[i].replacement.size(); j++) {
						if (rules[i].replacement[j] < 'A' || rules[i].replacement[j] > 'Z')
							cnt++;
						else if (marked[rules[i].replacement[j] - 'A'] == true)
							cnt++;
					}
					if (cnt == rules[i].replacement.size()) {
						ok = true;
						marked[rules[i].nonterminal - 'A'] = true;
					}
				}
			}
		} while (ok);

		// save the useless nonterminals for later use
		for (int i = 0; i < n; i++) {
			if (marked[i] == false && v.contains(i + 'A')) {
				useless.push_back(i + 'A');
			}
		}
		return;
	}

	void is_void() {
		useless_nonterminals();

		// check if the start symbol is useless
		for (size_t i = 0; i < useless.size(); i++) {
			if (useless[i] == start_symbol) {
				cout << "Yes\n";	
				return;
			}
		}

		cout << "No\n";
		return;
	}

void has_e() {
	
	int n = 'Z' - 'A' + 1;
	bool marked[n]; 
	for (size_t i = 0; i < n; i++) 
		marked[i] = false;

	bool ok = false;
	do {
		ok = false;
		for (size_t i = 0; i < rules.size(); i++) {
			// mark the nonterminal if the replacement is e 
			if (marked[rules[i].nonterminal - 'A'] == false) {
				if (rules[i].replacement == "e") {
					ok = true;
					marked[rules[i].nonterminal - 'A'] = true;
					if (rules[i].nonterminal == start_symbol) {
						cout << "Yes\n";
						return;
					}
				}
				/* count how many characters from the replacement 
				 generate e. If all of them do, mark the current 
				 nonterminal and continue */
				else {
					int cnt = 0;
					for (size_t j = 0; j < rules[i].replacement.size(); j++) {
						if (rules[i].replacement[j] >= 'A' && rules[i].replacement[j] <= 'Z')
							if (marked[rules[i].replacement[j] - 'A']) 
								cnt++;
					}
					if (cnt == rules[i].replacement.size()) {
						ok = true;		
						marked[rules[i].nonterminal - 'A'] = true;
						if (rules[i].nonterminal == start_symbol) {
							cout << "Yes\n";
							return;
						}
					}
				}
			}
		}
	} while (ok);

	if (marked[start_symbol - 'A']) 
		cout << "Yes\n";
	else 
		cout << "No\n";
	return; 
	}

	void answer_query(string option) {

		if (option == "--is-void") 
			is_void();

		else if (option == "--has-e")
			has_e();

		else if (option == "--useless-nonterminals") {
			useless_nonterminals();	
			for (size_t i = 0; i < useless.size(); i++) {
				printf("%c\n", useless[i]);
			}
		}
	}
};
