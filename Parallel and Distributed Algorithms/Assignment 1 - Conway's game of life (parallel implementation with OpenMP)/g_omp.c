#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <omp.h>

static const int MD = 50;

int main (int argc, char *argv[]) {

    if (argc != 4) {
        fprintf(stderr, "Usage: ./g_serial input_file no_of_iterations output_file\n");
        return -1;
    }

    FILE *f_in, *f_out;
    int n, c, l, i, j, sum;

    char input_file[MD], output_file[MD], ch;

    /* identify command line arguments */
    strcpy(input_file, argv[1]);
    strcpy(output_file, argv[3]);
    n = atoi(argv[2]);

    /* open input file and show message error 
       if it does not exist */
    f_in = fopen(input_file, "r");

    if (f_in == NULL) {
        fprintf(stderr, "Error opening input file\n");
        return -1;
    }

    /* read the dimensions of the automaton 
       and the matrix representing the initial state */
    fscanf(f_in, "%d %d", &l, &c);
    int **state = (int**)malloc((l + 2) * sizeof(int*));
    int **next_state = (int**)malloc((l + 2) * sizeof(int*));

    if (state == NULL || next_state == NULL) {
        fprintf(stderr, "Error allocating memory... Exiting.\n");
        return -1;
    }

    for (i = 0; i < l + 2; i++) {
        state[i] = (int*)malloc((c + 2) * sizeof(int));
        next_state[i] = (int*)malloc((c + 2) * sizeof(int));
        if (state[i] == NULL || next_state[i] == NULL) {
            fprintf(stderr, "Error allocating memory... Exiting.\n");
            return -1;
        }
    }

    ch = fgetc(f_in);
    i = 1, j = 1;

    while ((ch = fgetc(f_in)) != EOF) {

        char c = (char)ch;
        /* if a newline is read, increase the row number 
           and set the column number to 1 */
        if (c == '\n' ) {
            i++, j = 1;
            continue;
        }

        /* if a space is read, ignore it */
        if (c == ' ') 
            continue;
        
        /* if 'X' is read, store 1 in the state matrix;
           otherwise store 0 and increase the column number */
        (c == 'X') ? (state[i][j] = 1) : (state[i][j] = 0);
        j++;
    }

    /* close the input file */
    fclose(f_in);

    /* do n iterations of the algorithm */
    while (n-- > 0) {

        /* border the matrix */
        #pragma omp parallel for private(i) 
        for (i = 1; i < l + 1; i++) {
            state[i][0] = state[i][c];
            state[i][c + 1] = state[i][1];
        }

        #pragma omp parallel for private(j) 
        for (j = 1; j < c + 1; j++) {
            state[0][j] = state[l][j];
            state[l + 1][j] = state[1][j];
        }

        state[0][c + 1] = state[l][1];
        state[l + 1][0] = state[1][c];
        state[0][0] = state[l][c];
        state[l + 1][c + 1] = state[1][1];

        /* compute the next generation using 
            the current one */
        #pragma omp parallel for private(i, j, sum) 
        for (i = 1; i < l + 1; i++) {
            for (j = 1; j < c + 1; j++) {
                
                /* count how many neighbors are alive */
                sum = state[i - 1][j - 1] + state[i - 1][j + 1] 
                    + state[i + 1][j - 1] + state[i + 1][j + 1]
                    + state[i - 1][j] + state[i + 1][j]
                    + state[i][j - 1] + state[i][j + 1];

                /* apply the rules */
                if (state[i][j] == 1 && (sum < 2 || sum > 3)) 
                        next_state[i][j] = 0;
                if (state[i][j] == 1 && (sum == 2 || sum == 3)) 
                        next_state[i][j] = state[i][j];
                if (state[i][j] == 0 && sum == 3)
                        next_state[i][j] = 1;
                if (state[i][j] == 0 && sum != 3) 
                        next_state[i][j] = 0;
            }
        }

        /* copy next generation in current state matrix */
        #pragma omp parallel for private(i, j)
        for (i = 1; i < l + 1; i++) {
            for (j = 1; j < c + 1; j++) {
                state[i][j] = next_state[i][j];
            }
        }
    }

    /* open the output file */
    f_out = fopen(output_file, "w+");

    /* write the output */
    for (i = 1; i < l + 1; i++) {
        for (j = 1; j < c + 1; j++) {
            if (state[i][j] == 0)
                fprintf(f_out, ".");
            else 
                fprintf(f_out, "X");
        }
    if (i != l)
        fprintf(f_out, "\n");
    }
       
    /* close the output file */
    fclose(f_out);

    return 0;
}
