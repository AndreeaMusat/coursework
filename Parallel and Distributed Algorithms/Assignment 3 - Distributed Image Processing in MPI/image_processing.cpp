#include "image_processing.h"

#define TERMINATION_TAG 101

void print(vector<pair<int, int> > v)
{
	for (int i = 0; i < v.size(); i++)
		printf("%d --> %d,  ", v[i].first, v[i].second);
}

vector<pair<int, int> > get_limits(int buffer_size, int children)
{
	vector<pair<int, int> > limits;

	int chunk_size = ceil(1.0f * buffer_size / children); 
	if (chunk_size < 2)
	{
		chunk_size = 2;
		printf("CE MA FAC ?\n");
	}

	range (j, 0, children)
	{
		if (j == 0 && children == 1)
		{
			limits.pb(make_pair(0, buffer_size - 1));
		}
		else if (j == 0 && children > 1)
		{
			if (chunk_size * j < buffer_size)
				limits.pb(make_pair(chunk_size * j, min(chunk_size * (j + 1), buffer_size - 1)));
		}
		else if (j == children - 1 && j > 0)
		{
			if (chunk_size * j < buffer_size)
				limits.pb(make_pair(chunk_size * j - 1, min(chunk_size * (j + 1), buffer_size - 1)));
		}
		else 
		{
			if (chunk_size * j < buffer_size)
				limits.pb(make_pair(chunk_size * j - 1, min(chunk_size * (j + 1), buffer_size - 1)));
		}
	}
	return limits;
}

int main(int argc, char **argv) 
{
	if (argc != 4) 
	{
		cerr << "[Argument error]. Usage: ./filtru topologie.in imagini.in statistica.out. Exiting...\n";
		exit(EXIT_FAILURE);
	}

	int rank, nProcesses;

	MPI_Init(&argc, &argv);
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &nProcesses);

	FILE  *topo, *imag, *st;
	
	topo = fopen(argv[1], "r+");
	imag = fopen(argv[2], "r+");
	st = fopen(argv[3], "w+");

	if (topo == NULL || imag == NULL || st == NULL) 
	{
		cerr << "[File error]. File cannot be open. Exiting...\n";
		exit(EXIT_FAILURE);
	}

	Graph g;
	read_graph(g, topo);

	vector<query> queries;
	read_queries(queries, imag);	
	
	// STBAILIRE TOPOLOGIE ---------------------------------------------------------------------
	int noNodes = g.size();
	int parents[noNodes + 1];
	int recvParents[noNodes + 1];
	int parent = -1;

	MPI_Request req;
	MPI_Status stat;

	if (rank == 0)
	{
		range(i, 0, noNodes)
			parents[i] = -1;
		parents[noNodes] = rank;

		range(i, 0, g[rank].size())
		{
			MPI_Isend(&parents, noNodes + 1, MPI_INT, g[rank][i], 0, MPI_COMM_WORLD, &req);
			MPI_Wait(&req, &stat);
		}
	
		range(i, 0, g[rank].size()) 
		{
			MPI_Irecv(&recvParents, noNodes + 1, MPI_INT, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD, &req);
			MPI_Wait(&req, &stat);

			range(j, 0, noNodes) 
			{
				if (recvParents[j] != -1 && parents[j] == -1) {
					parents[j] = recvParents[j];
				}
			}
		}
	}
	else 
	{
		MPI_Irecv(&parents, noNodes + 1, MPI_INT, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD, &req);
		MPI_Wait(&req, &stat);
		
		parent = parents[noNodes];
		parents[rank] = parent;
		parents[noNodes] = rank;

		int i;
		range (i, 0, g[rank].size()) 
		{
			if (g[rank][i] != parent) 
				// continue;
			{
			MPI_Isend(&parents, noNodes + 1, MPI_INT, g[rank][i], 0, MPI_COMM_WORLD, &req);
			MPI_Wait(&req, &stat);
			}
		}

		range (i, 0, g[rank].size() - 1) 
		{
			MPI_Irecv(&recvParents, noNodes + 1, MPI_INT, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD, &req);
			MPI_Wait(&req, &stat);

			range (j, 0, noNodes) 
			{
				if (recvParents[j] != -1 && parents[j] == -1) 
				{
					parents[j] = recvParents[j];
				}
			}
		}

		MPI_Isend(&parents, noNodes + 1, MPI_INT, parent, 0, MPI_COMM_WORLD, &req);
		MPI_Wait(&req, &stat);
	}

	Graph mst(noNodes);

	if (rank == 0) 
	{
		range (i, 0, noNodes) 
		{
			if (parents[i] != -1)
				printf("node %d has parent %d\n", i, parents[i]);
			else 
				printf("node %d is root\n", i);
		}
		printf("\n");

		// trimit mst la toate nodurile 
		range (i, 0, noNodes)
		{
			MPI_Isend(&parents, noNodes + 1, MPI_INT, i, 0, MPI_COMM_WORLD, &req);	
			MPI_Wait(&req, &stat);
		}

		range (i, 0, noNodes)
			if (parents[i] != -1)
				mst[parents[i]].pb(i);
	}   
	else 
	{
		MPI_Irecv(&parents, noNodes + 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &req);
		MPI_Wait(&req, &stat);

		range (i, 0, noNodes)
			if (parents[i] != -1)
				mst[parents[i]].pb(i);
	}
	// ---------------- END STABILIRE TOPOLOGIE --------------------

	int no_of_lines_processed = 0; // TODO: statistica pt fiecare frunza

	range (i, 0, queries.size())
	{
		int column_size; // number of columns
		int buffer_size; // crt size of buffer sent/recved

		if (rank == 0) 
		{
			int *buffer = NULL;
			pgm_image img = read_pgm_image(queries[i].second.first);
			// print_pgm_image(img);

			column_size = img.n_col;
			buffer_size = img.n_row;

			vector<int> children_buff_sizes;
			vector<pair<int, int> > limits = get_limits(buffer_size, mst[rank].size());
			printf("ROOT: "); print(limits);
			
			buffer = new int[img.n_col * img.n_row];
			for (int j = 0; j < img.n_row; j++)
				for (int k = 0; k < img.n_col; k++)
					buffer[j * column_size + k] = img.image[j][k];


			// trimit chunk-uri
			range (j, 0, mst[rank].size())
			{
				// trimit dimensiunea coloanei
				MPI_Send(&column_size, 1, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);

				// trimit dimensiunea chunk-ului curent (nr de linii)
				int crt_buffer_size = 0;
				if (j < limits.size())
					crt_buffer_size = limits[j].second - limits[j].first + 1;
				
				children_buff_sizes.pb(crt_buffer_size);

				MPI_Send(&crt_buffer_size, 1, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);

				// daca dim buferului e nenula, voi trimite si bufferul
				if (crt_buffer_size > 0)
				{
					int start_index = limits[j].first * column_size;
					MPI_Send(&buffer[start_index], crt_buffer_size * column_size, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);
				}  
			}

			int useful_children = mst[rank].size() - std::count(children_buff_sizes.begin(), children_buff_sizes.end(), 0);
			// primesc chunk-urile procesate, elimin liniile granita
			range(j, 0, mst[rank].size())
			{
				if (children_buff_sizes[j] > 0)
				{
					int *new_buffer = new int[children_buff_sizes[j] * column_size];
					MPI_Recv(new_buffer, children_buff_sizes[j] * column_size, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
					
					// asamblez imaginea 
					if (useful_children == 1 && j == 0)
					{
						range(k, 0, children_buff_sizes[j] * column_size)
							buffer[k] = new_buffer[k];
					}
					else if (j == 0)
					{
						range(k, 0, (children_buff_sizes[j] - 1) * column_size)
							buffer[k] = new_buffer[k];
					}
					else if (j == useful_children - 1)
					{
						int buffer_start_index = (limits[j].first + 1) * column_size;
						int buffer_stop_index = buffer_start_index + (children_buff_sizes[j] - 1) * column_size;

						range(k, buffer_start_index, buffer_stop_index)
							buffer[k] = new_buffer[k - buffer_start_index + column_size];
					}
					else {
						int buffer_start_index = (limits[j].first + 1) * column_size;
						int buffer_stop_index = buffer_start_index + (children_buff_sizes[j] - 2) * column_size;

						range(k, buffer_start_index, buffer_stop_index)
							buffer[k] = new_buffer[k - buffer_start_index + column_size];
					}
				}
			}

			pgm_image new_image(buffer_size - 2, column_size - 2);
			new_image.comment = img.comment;
			range(j, 1, buffer_size - 1)
				range(k, 1, column_size - 1)
					new_image.image[j - 1][k - 1] = buffer[j * column_size + k];

			write_pgm_image_to_file(queries[i].second.second, new_image);

		}
		else 
		{
			int *buffer = NULL;
			int new_buffer_size = 0;

			// primesc dimensiunea coloanei de la nodul parinte
			MPI_Recv(&column_size, 1, MPI_INT, parents[rank], 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

			// primesc dimensiune chunk curent de la nodul parinte
			MPI_Recv(&buffer_size, 1, MPI_INT, parents[rank], 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			printf("Node %d received buffer_size = %d from parent %d\n", rank, buffer_size, parents[rank]);

			// primesc buffer daca dimensiunea sa este mai mare ca 0
			if (buffer_size > 0)
			{
				new_buffer_size = buffer_size * column_size;
				buffer = new int[new_buffer_size + 1];

				MPI_Recv(buffer, new_buffer_size, MPI_INT, parents[rank], 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			}  

			// daca sunt frunza, procesez
			if (mst[rank].size() == 0 && buffer_size > 0) 
			{
				no_of_lines_processed += buffer_size - 2;
				process_image(buffer_size, column_size, buffer, queries[i].first);

			 	// trimit imaginea procesata la parinte
				MPI_Send(buffer, new_buffer_size, MPI_INT, parents[rank], 0, MPI_COMM_WORLD);

				printf("Node %d finished\n", rank);

			} // daca nu sunt frunza, impart la fel ca root si trimit copiiilor
			else 
			{
				vector<int> children_buff_sizes;
				vector<pair<int, int> > limits = get_limits(buffer_size, mst[rank].size());
				printf("NODE %d: ", rank); print(limits);

				range(j, 0, mst[rank].size())
				{
					// trimit dimensiunea coloanei
					MPI_Send(&column_size, 1, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);	

					int crt_buffer_size = 0;
					if (j < limits.size())
						crt_buffer_size = limits[j].second - limits[j].first + 1;

					// salvez dimensiunea curenta a bufferului
					children_buff_sizes.pb(crt_buffer_size);

					// trimit dimensiunea chunk-ului curent (nr de linii)
					MPI_Send(&crt_buffer_size, 1, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);

					// daca dim bufferului e > 0, trimit bufferul
					if (crt_buffer_size > 0)
					{
						int start_index = limits[j].first * column_size;
						MPI_Send(&buffer[start_index], crt_buffer_size * column_size, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD);	
					}
				}

				int useful_children = mst[rank].size() - std::count(children_buff_sizes.begin(), children_buff_sizes.end(), 0);
			
				range(j, 0, mst[rank].size())
				{	
					if (children_buff_sizes[j] > 0)
					{
						// // primesc de la copil bufferul procesat
						int *new_buffer = new int[children_buff_sizes[j] * column_size];
						MPI_Recv(new_buffer, children_buff_sizes[j] * column_size, MPI_INT, mst[rank][j], 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
						
						if (useful_children == 1 && j == 0)
						{
							range(k, 0, children_buff_sizes[j] * column_size)
								buffer[k] = new_buffer[k];
						}
						else if (j == 0)
						{
							range(k, 0, (children_buff_sizes[j] - 1) * column_size)
								buffer[k] = new_buffer[k];
						}
						else if (j == useful_children - 1)
						{
							int buffer_start_index = (limits[j].first + 1) * column_size;
							int buffer_stop_index = buffer_start_index + (children_buff_sizes[j] - 1) * column_size;

							range(k, buffer_start_index, buffer_stop_index)
								buffer[k] = new_buffer[k - buffer_start_index + column_size];
						}
						else {
							int buffer_start_index = (limits[j].first + 1) * column_size;
							int buffer_stop_index = buffer_start_index + (children_buff_sizes[j] - 2) * column_size;

							range(k, buffer_start_index, buffer_stop_index)
								buffer[k] = new_buffer[k - buffer_start_index + column_size];
						}
					}	
				}
								
				if (buffer_size > 0)
					MPI_Send(buffer, buffer_size * column_size, MPI_INT, parents[rank], 0, MPI_COMM_WORLD);

				printf("Node %d finished\n", rank);
			} 
		}
	}

	fclose(topo);
	fclose(imag);
	fclose(st);	
	
	MPI_Finalize();
	return 0;
}

