#pragma once

#include "pgm_image.h"

int smooth_filter[] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 9};            
int blur_filter[] = {1, 2, 1, 2, 4, 2, 1, 2, 1, 16};           
int sharpen_filter[] = {0, -2, 0, -2, 11, -2, 0, -2, 0, 3}; 
int mean_removal_filter[] = {-1, -1, -1, -1, 9, -1, -1, -1, -1, 1};   
		
enum filter_name
{
	SMOOTH, BLUR, SHARPEN, MEAN_REMOVAL
};

void print_graph(Graph);
void read_graph(Graph&, FILE*);
void read_queries(vector<query>&, FILE*);
pgm_image read_pgm_image(string, pgm_image&);

pgm_image read_pgm_image(string image_name) 
{
	int cols, rows;
	string line;
	stringstream ss;
	ifstream fin(image_name.c_str());

	if (!fin.is_open())
	{
		cerr << "Image file could not be open. Exiting...\n";
		exit(EXIT_FAILURE);
	}

	// First line: "P2"
	getline(fin, line);
	if (line.compare("P2") != 0)
	{
		cerr << "File format error. Exiting...";
		exit(EXIT_FAILURE);
	}

	// Second line: some comment
	string comment;
	getline(fin, comment);
	cout << "COMMENT IS: " << comment << "\n";

	// Third line: no of colums, no of rows
	ss << fin.rdbuf();
	ss >> cols >> rows;

	int max_val;
	ss >> max_val;

	pgm_image img = pgm_image(rows + 2, cols + 2);
	img.comment = comment;

	// Next lines: the image
	for (int i = 1; i <= rows; i++)
		for (int j = 1; j <= cols; j++)
			ss >> img.image[i][j];

	fin.close();
	return img;
}

void write_pgm_image_to_file(string file_name, pgm_image img)
{
	ofstream fout(file_name.c_str());

	if (!fout.is_open())
	{
		cerr << "Image file could not be open. Exiting...\n";
		exit(EXIT_FAILURE);
	}

	fout << "P2\n";
	fout << img.comment << "\n";
	fout << img.n_col << " " << img.n_row << "\n";
	fout << 255 << "\n";

	for (int i = 0; i < img.n_row; i++) 
	{
		for (int j = 0; j < img.n_col; j++)
			fout << img.image[i][j] << "\n";
		// fout << "\n";
	}

	fout.close();
}

// to delete
void print_pgm_image(pgm_image img)
{
	for (int i = 0; i < img.n_row; i++)
	{
		for (int j = 0; j < img.n_col; j++)
			printf("%d ", img.image[i][j]);
		printf("\n");
	}
}

// to del
void print_graph(Graph g) 
{
	for (size_t i = 0; i < g.size(); i++)
	{
		printf("%lu: ", i);
		for (size_t j = 0; j < g[i].size(); j++)
		{
			printf("%d ", g[i][j]);
		}
		printf("\n");
	}
}

void read_graph(Graph& g, FILE *in) 
{
	ssize_t read;
	size_t len = 0;
	char *line = NULL;

	while ((read = getline(&line, &len, in)) != -1)
	{
		int node;
		sscanf(line, "%d", &node);
   		char *str = strchr(line, ':');

        string crt_line = string(str + 1);
        string buffer;
        stringstream ss(crt_line);
      
        vector<int> crt;
        while(ss >> buffer)
        	crt.pb(atoi(buffer.c_str()));
        g.pb(crt);
	}
}

void read_queries(vector<query>& queries, FILE *in)
{
	int N;
	fscanf(in, "%d", &N);
	range(i, 0, N) 
	{
		char file_name[MAXDIM], filter[MAXDIM], output_name[MAXDIM];
		fscanf(in, "%s %s %s", filter, file_name, output_name);
		queries.pb(mtp(string(filter), string(file_name), string(output_name)));
	}
	
	return;
}

void process_image(int n, int m, int *array, string filter_name)
{
	int old_array[n * m];
	range(i, 0, n)
		range(j, 0, m)
			old_array[i * m + j] = array[i * m + j];

	int *filter;
	if (filter_name.compare("smooth") == 0) filter = smooth_filter;
	else if (filter_name.compare("blur") == 0) filter = blur_filter;
	else if (filter_name.compare("sharpen") == 0) filter = sharpen_filter;
	else if (filter_name.compare("mean_removal") == 0) filter = mean_removal_filter;
	else 
	{
		cerr << "Filter name not known. Exiting...\n";
		exit(EXIT_FAILURE);
	}

	range(i, 1, n - 1)
	{
		range(j, 1, m - 1)
		{
			int sum = 0;
			range(ii, i - 1, i + 2) 
				range(jj, j - 1, j + 2)
					sum += old_array[ii * m + jj] * filter[3 * abs(i - 1 - ii) + abs(j - 1 - jj)];

			array[i * m + j] = sum / filter[9];
			if (array[i * m + j] > 255)
				array[i * m + j] = 255;
			if (array[i * m + j] < 0)
				array[i * m + j] = 0;
		}
	}
}