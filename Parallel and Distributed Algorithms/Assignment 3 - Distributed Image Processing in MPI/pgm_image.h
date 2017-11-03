#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>
#include <utility>
#include <sstream>
#include <string>
#include <fstream>
#include <algorithm>
#include <cmath>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <mpi.h>

#define query pair<string, pair<string, string> >
#define mtp(a, b, c) make_pair(a, make_pair(b, c))
#define Graph vector<vector<int> >
#define pb push_back
#define range(i, a, b) for(int i = a; i < b; i++)
#define MAXDIM 100
#define filter_size 9
using namespace std;


class pgm_image 
{
public:
	int n_row, n_col;
	int **image;
	string comment;

	pgm_image() {}

	pgm_image(int n_row, int n_col): n_row(n_row), n_col(n_col) 
	{
		image = new int*[n_row];
		for (int i = 0; i < n_row; i++)
			image[i] = new int[n_col];
		
		for (int i = 0; i < n_row; i++)
			for (int j = 0; j < n_col; j++)
				image[i][j] = 0;
	}
};