#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "nokia5110.h"

#define DOWN PD3
#define LEFT PD0
#define UP PD2
#define RIGHT PD4
#define CENTER PD1
#define DIM 30

// buttons stuff
inline void setup_buttons()
{
	DDRD &= (1 << UP);
	DDRD &= (1 << DOWN);
	DDRD &= (1 << LEFT);
	DDRD &= (1 << RIGHT);
	DDRD &= (1 << CENTER);

	PORTD |= (1 << UP);
	PORTD |= (1 << DOWN);
	PORTD |= (1 << LEFT);
	PORTD |= (1 << RIGHT);
	PORTD |= (1 << CENTER);
}

inline void setup_lcd()
{
	nokia_lcd_init();
	nokia_lcd_clear();
	nokia_lcd_set_cursor(10, 10);
	nokia_lcd_write_string("NIM", 4);
	nokia_lcd_render();
	_delay_ms(1500);
	nokia_lcd_clear();
}

inline bool is_pressed(uint8_t btn)
{
	return (PIND & (1 << btn)) == 0 ? true : false;
}

inline void check_buttons()
{
	while (1)
	{
		if (is_pressed(DOWN))
		{
			nokia_lcd_clear();
			nokia_lcd_write_string("DOWN", 1);
			nokia_lcd_render();
			_delay_ms(1000);
			nokia_lcd_clear();
		}

		else if (is_pressed(RIGHT))
		{
			nokia_lcd_clear();
			nokia_lcd_write_string("RIGHT", 1);
			nokia_lcd_render();
			_delay_ms(1000);
			nokia_lcd_clear();
		}

		else if (is_pressed(LEFT))
		{
			nokia_lcd_clear();
			nokia_lcd_write_string("LEFT", 1);
			nokia_lcd_render();
			_delay_ms(1000);
			nokia_lcd_clear();
		}

		else if (is_pressed(CENTER))
		{
			nokia_lcd_clear();
			nokia_lcd_write_string("CENTER", 1);
			nokia_lcd_render();
			_delay_ms(1000);
			nokia_lcd_clear();
		}

		else if (is_pressed(UP))
		{
			nokia_lcd_clear();
			nokia_lcd_write_string("UP", 1);
			nokia_lcd_render();
			_delay_ms(1000);
			nokia_lcd_clear();
		}
	}
}

// nim stuff
#define max(a, b) (a >= b) ? a : b
#define min(a, b) (a <= b) ? a : b
static const int computer = 0;
static const int human = 1;

struct nim_game_t
{
	int *piles;
	int no_of_piles;
	int player;
	int ai;
	int easy;
} nim;

struct nim_move_t
{
	int pile_no;
	int count;
};

typedef struct nim_move_t move;

void display_game(int pile)
{
	int i, cnt, xcoord;

	if (nim.no_of_piles == 3)
		xcoord = 15;
	if (nim.no_of_piles == 4)
		xcoord = 7;
	if (nim.no_of_piles == 5)
		xcoord = 0;

	nokia_lcd_clear();
	nokia_lcd_set_cursor(xcoord, 0);
	for (cnt = 0; cnt <= 5; cnt++)
	{
		for (i = 0; i < nim.no_of_piles; i++)
		{
			if (nim.piles[i] >= cnt)
				nokia_lcd_write_string(" o ", 1);
			else 
				nokia_lcd_write_string("   ", 1);
		}
		nokia_lcd_set_cursor(xcoord, 8 * cnt);
	}

	if (pile >= 0 && pile < nim.no_of_piles)
	{
		nokia_lcd_set_cursor(xcoord + 18 * pile + 6, 40);
		nokia_lcd_write_string("_", 1);
	}

	nokia_lcd_render();	
}

int compute_nim_sum()
{
	int i;
	int sum = nim.piles[0];
	for (i = 1; i < nim.no_of_piles; i++)
		sum ^= nim.piles[i];
	return sum;
}

void make_move()
{
	_delay_ms(1500);
	move mv;
	int i;
	int nim_sum;

	nim_sum = compute_nim_sum();
	
	// daca nim sum != 0 as putea castiga
	if (nim.easy == 1 && nim_sum != 0)
	{
		for (i = 0; i < nim.no_of_piles; i++)
		{
			if ((nim.piles[i] ^ nim_sum) < nim.piles[i])
			{
				mv.pile_no = i;
				mv.count = nim.piles[i] - (nim.piles[i] ^ nim_sum);
				nim.piles[i] ^= nim_sum;
				return;
			}
		}
	}
	// altfel pierd oricum daca oponentul joaca optim, 
	// asa ca fac o mutare random
	else 
	{
		int random_pile = rand() % nim.no_of_piles;
		while (nim.piles[random_pile] == 0)
			random_pile = rand() % nim.no_of_piles;
		mv.pile_no = random_pile;
		mv.count = (rand() % nim.piles[random_pile]) + 1;
		nim.piles[mv.pile_no] -= mv.count;
		if (nim.piles[mv.pile_no] < 0)
			nim.piles[mv.pile_no] = 0;
		return;
	}
}

bool is_game_over()
{
	int i;
	for (i = 0; i < nim.no_of_piles; i++)
		if (nim.piles[i] != 0)
			return false;
	return true;
}

void print_players_menu(int players)
{
	nokia_lcd_init();
	nokia_lcd_clear();

	if (players == 1)
		nokia_lcd_write_string("SINGLEPLAYER *", 1);
	else
		nokia_lcd_write_string("singleplayer", 1);

	nokia_lcd_set_cursor(0, 10);
	nokia_lcd_write_string("_____________", 1);
	nokia_lcd_set_cursor(0, 25);

	if (players == 1)
		nokia_lcd_write_string("multiplayer", 1);
	else
		nokia_lcd_write_string("MULTIPLAYER *", 1);

	nokia_lcd_render();
	_delay_ms(10);
}

void print_customizable_menu(int customizable)
{
	nokia_lcd_clear();

	if (customizable == 0)
		nokia_lcd_write_string("RANDOM *", 1);
	else
		nokia_lcd_write_string("random ", 1);

	nokia_lcd_set_cursor(0, 10);
	nokia_lcd_write_string("_____________", 1);
	nokia_lcd_set_cursor(0, 25);

	if (customizable == 0)
		nokia_lcd_write_string("customized", 1);
	else 
		nokia_lcd_write_string("CUSTOMIZED *", 1);

	nokia_lcd_render();
}

void print_difficulty(int difficulty)
{
	nokia_lcd_clear();

	if (difficulty == 0)
		nokia_lcd_write_string("EASY *", 1);
	else
		nokia_lcd_write_string("easy ", 1);

	nokia_lcd_set_cursor(0, 10);
	nokia_lcd_write_string("_____________", 1);
	nokia_lcd_set_cursor(0, 25);

	if (difficulty == 0)
		nokia_lcd_write_string("hard", 1);
	else 
		nokia_lcd_write_string("HARD *", 1);

	nokia_lcd_render();
}

void init_piles()
{
	nim.no_of_piles = 3;
	
	nim.piles = (int*) calloc(5, sizeof(int));
	for (int i = 0; i < 5; i++)
		nim.piles[i] = rand() % 5 + 1;

	nim.player = human;
}

void print_game_setup(int btn)
{
	char buffer[DIM];
	nokia_lcd_clear();
	memset(buffer, 0, DIM);
	sprintf(buffer, "Piles: %d", nim.no_of_piles);
	if (btn == 0) strcat(buffer, " *");
	nokia_lcd_write_string(buffer, 1);
	for (int i = 0; i < nim.no_of_piles; i++)
	{
		memset(buffer, 0, DIM);
		sprintf(buffer, "Pile %d has %d", i, nim.piles[i]);
		if (btn - 1 == i) strcat(buffer, " *");
		nokia_lcd_set_cursor(0, (i + 1) * 8);
		nokia_lcd_write_string(buffer, 1);
	}
	nokia_lcd_render();
}

void play_game()
{
	while (!is_game_over())
	{
		// iau input daca nu folosesc ai sau 
		// daca folosesc ai dar e randul jucatorului
		if (!nim.ai or 
			(nim.ai && nim.player == human))
		{
			int pile = 0;
			int removed = 0;
			bool chose_pile = false;
			bool ready = false;

			display_game(pile);
			while (!ready)
			{
				if (is_pressed(LEFT) && chose_pile == false)
				{
					pile = (pile + nim.no_of_piles - 1) % nim.no_of_piles;
					display_game(pile);
					_delay_ms(300);
				}

				if (is_pressed(RIGHT) && chose_pile == false)
				{
					pile = (pile + 1) % nim.no_of_piles;
					display_game(pile);
					_delay_ms(300);
				}

				if (is_pressed(CENTER) && chose_pile == true)
				{
					nim.piles[pile] = max(0, nim.piles[pile] - 1);
					removed++;
					display_game(pile);
					_delay_ms(300);
				}

				if (is_pressed(CENTER) && chose_pile == false)
				{
					chose_pile = true;
					_delay_ms(300);
				}

				if ((is_pressed(LEFT) || is_pressed(RIGHT)) && removed > 0)
				{
					ready = true;
					_delay_ms(300);
				}
			}
		}
		// altfel ai-ul face o mutare
		else 
		{	
			display_game(-1);
			make_move();
		}

		// schimb jucatorul
		nim.player = 1 - nim.player;
		_delay_ms(700);
	}

	display_game(-1);
	nokia_lcd_clear();
	if (!nim.ai)
	{
		if (nim.player == 0)
			nokia_lcd_write_string("Player 1 won.", 1);
		else 
			nokia_lcd_write_string("Player 0 won.", 1);
	}

	else 
	{
		if (nim.player == computer)
			nokia_lcd_write_string("YOU won", 2);
		else 
			nokia_lcd_write_string("AI won", 2);
	}

	nokia_lcd_render();
}

int main()
{
	int players;
	int menu_btn;
	bool ready;
	int customizable;

	setup_buttons();
	setup_lcd();

	players = 1;
	ready = false;
	print_players_menu(players);

	while (!ready)
	{
		if (is_pressed(RIGHT) || is_pressed(LEFT))
		{
			players = 1 - players;
			print_players_menu(players);
			_delay_ms(300);
		}

		if (is_pressed(CENTER))
		{
			ready = true;
			_delay_ms(200);
		}
	}

	ready = false;
	nim.easy = 0;
	print_difficulty(nim.easy);
	while (!ready)
	{
		if (is_pressed(RIGHT) || is_pressed(LEFT))
		{
			nim.easy = 1 - nim.easy;
			print_difficulty(nim.easy);
			_delay_ms(300);
		}

		if (is_pressed(CENTER))
		{
			ready = true;
			_delay_ms(200);
		}
	}

	nim.ai = players;
	ready = false;
	customizable = 0;
	print_customizable_menu(customizable);
	while (!ready)
	{
		if (is_pressed(RIGHT) || is_pressed(LEFT))
		{
			customizable = 1 - customizable;
			print_customizable_menu(customizable);
			_delay_ms(300);
		}

		if (is_pressed(CENTER))
		{
			ready = true;
			_delay_ms(200);
		}
	}

	init_piles();
	menu_btn = 0;
	print_game_setup(menu_btn);
	if (customizable == 1)
	{
		ready = false;
		while (!ready)
		{
			if (is_pressed(LEFT))
			{
				if (menu_btn == 0)
					nim.no_of_piles = max(3, nim.no_of_piles - 1);
				else 
					nim.piles[menu_btn - 1] = max(1, nim.piles[menu_btn - 1] - 1);

				print_game_setup(menu_btn);
				_delay_ms(300);
			}

			if (is_pressed(RIGHT))
			{
				if (menu_btn == 0)
					nim.no_of_piles = min(5, 1 + nim.no_of_piles);
				else
					nim.piles[menu_btn - 1] = min(5, 1 + nim.piles[menu_btn - 1]);

				print_game_setup(menu_btn);

				_delay_ms(300);
			}

			if (is_pressed(CENTER))
			{
				menu_btn = (menu_btn + 1);
				if (menu_btn == 1 + nim.no_of_piles)
					ready = true;
				print_game_setup(menu_btn);
				_delay_ms(200);
			}
		}	
	}

	display_game(-1);
	play_game();
}