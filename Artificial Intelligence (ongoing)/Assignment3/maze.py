import sys
import random
from copy import deepcopy

# gate index
POS, NUM_DEST, LIST_DEST = 0, 1, 2

# list dest index
POS, PROB = 0, 1

# config indices
MAZE_SIZE, INIT_POS, FINAL_POS, GATES, MAZE = 0, 1, 2, 3, 4
INF = 99999999
delta_neighbors = [(1, 0), (0, 1), (-1, 0), (0, -1)]

def read_input(filename):
	try:
		file = open(filename, "r")
	except Exception:
		print("[Error] Could not open input file")
		sys.exit(-1)

	N, M, T = tuple([int(x) for x in next(file).split()])
	initial_pos = tuple(reversed([int(x) for x in next(file).split()]))
	final_pos = tuple(reversed([int(x) for x in next(file).split()]))
	
	gates, maze = [], []
	for i in range(T):
		words = next(file).split()
		x_t, y_t, k = tuple([int(x) for x in words[0:3]])
		list_dest = []
		for i in range(k):
			x_i, y_i = tuple([int(x) for x in words[(i + 1) * 3:(i + 1) * 3 + 2]])
			p_i = float(words[(i + 1) * 3 + 2])
			list_dest.append(((y_i, x_i), p_i))

		curr_gate = ((y_t, x_t), k, list_dest)
		gates.append(curr_gate)
	
	for line in file:
		maze.append(list(line.rstrip()))

	config = [(N, M), initial_pos, final_pos, gates, maze]
	return config

def manhattan_distance(start, end):
	dx = abs(start[0] - end[0])
	dy = abs(start[1] - end[1])
	return dx + dy

def construct_path(parents, end_pos, gate_pos):
	path = [end_pos]
	curr_point = end_pos
	while curr_point in parents:
		curr_point = parents[curr_point]
		path = [curr_point] + path
		
	count_portals = 0
	for gate in gate_pos:
		while gate in path:
			path.remove(gate)
			count_portals += 1

	return path

def probabilistic_heuristic(config):
	# initialize the probabilistic heuristic matrix 
	# with the Manhattan distances to the final position
	bfs_scores = []
	for i in range(config[MAZE_SIZE][0]):
		curr_l = []
		for j in range(config[MAZE_SIZE][1]):
			curr_l.append(manhattan_distance((i, j), config[FINAL_POS]))
		bfs_scores.append(curr_l)

	# then for every portal, the score will be the weighted
	# average of its destiations
	for entry in config[GATES]:
		gate_pos = entry[POS]
		num_dest = entry[NUM_DEST]
		dest = entry[LIST_DEST]
		
		gate_score = 0
		for i in range(num_dest):
			dest_point = dest[i][0]
			dest_prob = dest[i][PROB]
			curr_score = bfs_scores[dest_point[0]][dest_point[1]]
			curr_score *= dest_prob
			gate_score += curr_score
		bfs_scores[gate_pos[0]][gate_pos[1]] = gate_score

	return bfs_scores

def get_random_neighbor(point, config):

	# find the portal having the coordinates the same as point
	curr_gate_info = None
	for entry in config[GATES]:
		if entry[POS] == point:
			curr_gate_info = entry
			break

	# create a cumulative vector of the probabilities.
	destinations_probs = [t[1] for t in entry[LIST_DEST]]
	for i in range(1, len(destinations_probs)):
		destinations_probs[i] += destinations_probs[i - 1]

	# get a random number between 0 and 1 and the corresponing 
	# destination is the first that has the cumulative probability
	# greater than the random number 
	rand_no = random.random()
	first_ge = list(filter(lambda p : p >= rand_no, destinations_probs))[0]
	neighbor_index = destinations_probs.index(first_ge)
	return entry[LIST_DEST][neighbor_index][0]

def a_star(config, heuristic, probabilistic, use_portals=False):
	N, M = config[MAZE_SIZE]
	gates_pos = [t[0] for t in config[GATES]]

	parents, closed_set, open_set = {}, [], [config[INIT_POS]]
	g_score = [[INF for j in range(M)] for i in range(N)]
	f_score = [[INF for j in range(M)] for i in range(N)]

	start_end_dist = heuristic(config[INIT_POS], config[FINAL_POS])
	g_score[config[INIT_POS][0]][config[INIT_POS][1]] = 0
	f_score[config[INIT_POS][0]][config[INIT_POS][1]] = start_end_dist

	while len(open_set) > 0:
		curr_point = min(open_set, key=lambda point : f_score[point[0]][point[1]])
		if curr_point == config[FINAL_POS]:
			return construct_path(parents, config[FINAL_POS], gates_pos)

		open_set.remove(curr_point)
		closed_set.append(curr_point)

		if probabilistic == True and curr_point in gates_pos:
			neighbors = [get_random_neighbor(curr_point, config)]
		else:
			neighbors = [(curr_point[0] + neigh[0], curr_point[1] + neigh[1]) \
							for neigh in delta_neighbors]

		for neighbor in neighbors:

			if config[MAZE][neighbor[0]][neighbor[1]] == 'X':
				continue

			if neighbor in closed_set:
				continue

			if use_portals == False and neighbor in gates_pos:
				continue
			
			if neighbor not in open_set:
				open_set.append(neighbor)

			new_g_score = g_score[curr_point[0]][curr_point[1]] + 1
			if new_g_score >= g_score[neighbor[0]][neighbor[1]]:
				continue

			heuristic_estimate = heuristic(neighbor, config[FINAL_POS])
			parents[neighbor] = curr_point
			g_score[neighbor[0]][neighbor[1]] = new_g_score
			f_score[neighbor[0]][neighbor[1]] = new_g_score + heuristic_estimate

	return None

def collect_data(config, steps=1000):
	info = {}
	gates_pos = [t[0] for t in config[GATES]]
	gates_idx = 0
	curr_point = config[INIT_POS]
	copy_config = deepcopy(config)

	# while there are remaining steps left to explore, go
	# to the next portal and update the probability 
	# distribution of the destination (the number of times
	# the agent was teleported to that destination, actually)
	while steps > 0:
		curr_portal = gates_pos[gates_idx]
		copy_config[FINAL_POS] = curr_portal
		copy_config[INIT_POS] = curr_point
		path = a_star(copy_config, manhattan_distance, False, use_portals=True)
		steps -= len(path) - 1
		
		portal_destination = get_random_neighbor(curr_portal, config)

		if curr_portal not in info:
			info[curr_portal] = {}
		if portal_destination in info[curr_portal]:
			info[curr_portal][portal_destination] += 1
		else:
			info[curr_portal][portal_destination] = 1

		curr_point = portal_destination
		gates_idx = (gates_idx + 1) % len(gates_pos)

	for portal in info:
		total_simulations = 0
		for destination in info[portal]:
			total_simulations += info[portal][destination]
		for destination in info[portal]:
			info[portal][destination] *= 1.0
			info[portal][destination] /= total_simulations

	list_dest = [(portal, len(info[portal]), [(dest, info[portal][dest]) for dest in info[portal]]) for portal in info]
	config[GATES] = list_dest	

def run_a_star(config, heuristic_func, probabilistic, use_portals, num_rounds=1, verbose=False):
	# run num_rounds simulations of a*
	count = 0
	average_num_moves = 0.0
	while count < num_rounds:
		res = a_star(config, heuristic_func, probabilistic, use_portals=use_portals)
		if res is not None:
			if verbose:
				print("Path len = ", len(res) - 1)
				print(res)
			average_num_moves += len(res) - 1
		else:
			if verbose:
				print("Could not find any path")
		count += 1

	average_num_moves /= num_rounds
	return average_num_moves

def main(args):
	if len(args) != 2:
		print("[Error] Usage: python maze.py input_file")
		sys.exit(-1)

	filename = args[1]
	config = read_input(filename)
	
	# Simple Manhattan distance heuristic (Task 1)
	simple_result = run_a_star(config, manhattan_distance, False, False)
	print("Simple A* expected path length =", simple_result)

	# Compute expected value of the length of the path knowing the probabilities (Task 2)
	num_rounds = 1000
	scores = probabilistic_heuristic(config)
	prob_heuristic = lambda start, end : scores[start[0]][start[1]]
	probabilistic_result = run_a_star(config, prob_heuristic, True, True, num_rounds=num_rounds)
	print("Probabilistic A* expected path length = ", probabilistic_result)

	# Compute expected value of the length of the path without knowing the destinations
	# of the portals and their probabilities (Task 3)
	for steps in [100, 1000, 10000]:
		copy_config = deepcopy(config)
		collect_data(copy_config, steps=steps)
		result = run_a_star(copy_config, prob_heuristic, True, True, num_rounds=num_rounds)
		print("Using", steps, "exploration steps, the probabilistic A* expected path length is", result)
	

if __name__ == "__main__":
	main(sys.argv)
