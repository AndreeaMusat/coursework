from util import *
import argparse

best_sol_cost, best_sol = INF, None
total_time = INF

def toposort_tasks(state):
	graph, in_degree, score, queue = {}, {}, {}, []

	# initialize in_degree (no of tasks that still have to be solved before curr task)
	# assign each node a score of 1
	# create a queue of nodes with in-degree 0
	for task_idx in state.to_schedule:
		graph[task_idx] = []

		func = lambda task_idx : state.tasks[task_idx].scheduled_time == None
		not_scheduled_prev_tasks = list(filter(func, state.tasks[task_idx].prev_tasks))
		in_degree[task_idx] = len(not_scheduled_prev_tasks)

		if in_degree[task_idx] == 0:
			queue.append(task_idx)

		score[task_idx] = 0

	# create graph (directed from prev task to current task)
	for task_idx in state.to_schedule:
		task = state.tasks[task_idx]
		for prev_task_idx in task.prev_tasks:
			if state.tasks[prev_task_idx].scheduled_time != None:
				continue
			graph[prev_task_idx].append(task.index)

	max_level = 0
	# compute scores 
	while queue != []:
		top_elem = queue.pop(0)
		for neighbour in graph[top_elem]:
			
			in_degree[neighbour] -= 1
			score[neighbour] = max(score[neighbour], 1 + score[top_elem])
			max_level = max(max_level, score[neighbour])
			if in_degree[neighbour] == 0:
				queue.append(neighbour)

	# deadline score = min deadline reachable from current node
	deadline_score = {}

	for task_idx in state.to_schedule:
		deadline_score[task_idx] = state.tasks[task_idx].deadline

	for level in range(max_level - 1, -1, -1):
		for task_idx in state.to_schedule:
			if score[task_idx] != level:
				continue
			dl_scores_out = []
			for neighbour_idx in graph[task_idx]:
				if score[neighbour_idx] == level + 1:
					dl_scores_out.append(deadline_score[neighbour_idx])
			if dl_scores_out != []:
				deadline_score[task_idx] = min(min(dl_scores_out), deadline_score[task_idx])
	
	state.to_schedule.sort(key=lambda t : (score[t], deadline_score[t], state.tasks[t].duration))

def bktSearch(state, sort_procs, sort_dls, use_arc_consistency, sort_tasks):
	global best_sol_cost, best_sol, total_time

	# compute current solution cost and return if greater than best cost
	curr_sol_cost = state.getSolutionCost()
	if curr_sol_cost >= best_sol_cost:
		return

	# update best solution if valid solution was found
	if state.isFinalState():
		if state.isSolutionValid(-1):
			best_sol = state
			best_sol_cost = curr_sol_cost
		else:
			return
	
	# return if no time left
	total_time -= 1
	if total_time <= 0:
		return

	# sort the processors by their first available time
	if sort_procs:
		procs = sorted(state.procs.items(), key=lambda p : state.getFirstAvailableTime(p[0]))
	else:
		procs = sorted(state.procs.items(), key=lambda p : p[0])

	# sort tasks by their deadline
	if sort_dls:
		len_solved_dependencies = lambda task_idx : \
				(state.tasks[task_idx].deadline, 
					len(list(filter(lambda t : state.tasks[t].scheduled_time == None, \
						state.tasks[task_idx].prev_tasks))))
		state.to_schedule.sort(key = len_solved_dependencies)

	# topological sort of tasks
	if sort_tasks:
		toposort_tasks(state)	
		
	# try to schedule each task on each processor 
	for task_idx in state.to_schedule:
		curr_task = state.tasks[task_idx]
		
		for i in range(len(procs)):
			proc_idx = procs[i][0]
		
			cond = False
			if not use_arc_consistency:
				cond = True
			elif state.isConsistent(curr_task, proc_idx):
				cond = True

			# if state is valid, search values for the remaining variables
			if cond:
				new_state = deepcopy(state)
				new_state.scheduleTask(curr_task.index, proc_idx)
				if new_state.isSolutionValid(curr_task.index):
					bktSearch(new_state, sort_procs, sort_dls, use_arc_consistency, sort_tasks)

				if total_time <= 0:
					return

def main(args):

	sys.setrecursionlimit(3000)

	# read input from file
	if len(args) < 3:
		print("Usage: python3 <name of this file> input budget [--sort-dls | --sort-tasks | --arc-consistency | --sort-procs] ", file=sys.stderr)
		return

	global total_time
	filename = args[1]
	total_time = int(args[2])

	try:
		input_file = open(filename, 'r')
	except OSError:
		print("Cannot open input file. Exiting", file=sys.stderr)
		return 

	# read input file and create initial state
	line = input_file.readline()
	[N, P] = list(map(int, line.split(',')))
	tasks = {}
	while True:
		line = input_file.readline().rstrip('\n')
		if not line:
			break
		nums = list(map(int, line.split(',')))
		index, duration, deadline = nums[0], nums[1], nums[2]
		prev_tasks = list(map(lambda x: x - 1, nums[3:]))
		tasks[index - 1] = (Task(index - 1, duration, deadline, prev_tasks))

	state = State(P, tasks)

	# parse search options
	sort_procs, sort_dls, use_arc_consistency, sort_tasks = False, False, False, False

	for i in range(3, len(args)):
		if args[i] == "--sort-procs":
			sort_procs = True
		elif args[i] == "--sort-dls":
			sort_dls = True
		elif args[i] == "--arc-consistency":
			use_arc_consistency = True
		elif args[i] == "--sort-tasks":
			sort_tasks = True
		else:
			print("Unknown option %s. Exiting", args[i])
			sys.exit(1)

	# search
	bktSearch(state, sort_procs, sort_dls, use_arc_consistency, sort_tasks)

	# print solution
	if best_sol != None:
		print(best_sol)

if __name__ == "__main__":
	main(sys.argv)
