import sys
import operator
from copy import deepcopy
INF = 99999999999999

class Task(object):
	def __init__(self, index, duration, deadline, prev_tasks=[]):
		self.index = index
		self.duration = duration
		self.deadline = deadline
		self.prev_tasks = prev_tasks
		self.scheduled_time = None
		self.scheduled_proc = None

	def __str__(self):
		return "Task %d, duration = %d, deadline = %d, prev_tasks = " % \
			(self.index, self.duration, self.deadline) + str(self.prev_tasks)

	def getFinishTime(self):
		if self.scheduled_time == None:
			return None
		return self.scheduled_time + self.duration

	def getCost(self):
		if self.scheduled_time == None:
			return None
		return max(0, self.getFinishTime() - self.deadline)

class State(object):
	"""
	procs = a dictionary of num_procs lists
	procs[i] = a list containing the (ordered) indices of tasks that have been scheduled on processor i
	tasks = a list of Task objects containing all the tasks
	to_schedule = tasks that haven't been scheduled yet
	"""
	def __init__(self, num_procs, tasks):
		self.procs = {}
		for i in range(num_procs):
			self.procs[i] = []

		self.tasks = tasks
		self.to_schedule = list(map(lambda task : task.index, tasks.values()))

	def __str__(self):
		res = ""
		for proc_idx in range(len(self.procs)):
			res += str(len(self.procs[proc_idx])) + "\n"
			for task_idx in self.procs[proc_idx]:
				res += str(task_idx + 1) + "," + str(self.tasks[task_idx].scheduled_time) + "\n"
		return res

	def getSolutionCost(self):
		total_cost = 0
		for proc_idx in range(len(self.procs)):
			for i in range(len(self.procs[proc_idx])):
				task_idx = self.procs[proc_idx][i]
				total_cost += self.tasks[task_idx].getCost()
		return total_cost

	def isFinalState(self):
		return self.to_schedule == []

	def isValid(self, scheduled_task_idx):
		scheduled_task = self.tasks[scheduled_task_idx]
		for prev_task in self.tasks[scheduled_task.index].prev_tasks:
			prev_task_finish_time = self.tasks[prev_task].getFinishTime()
			curr_task_start_time = self.tasks[scheduled_task.index].scheduled_time
			
			# if previous task was not scheduled at all, ignore it
			if prev_task_finish_time is None:
				continue

			# if prev task was scheduled but its finish time is greater than curr task start time, return False
			if prev_task_finish_time > curr_task_start_time:
				return False
		return True

	def isSolutionValid(self, scheduled_task_idx_arg = -1):
		if scheduled_task_idx_arg == -1:
			for proc_idx in range(len(self.procs)):
				for scheduled_task_idx in self.procs[proc_idx]:
					if self.isValid(scheduled_task_idx) == False:
						return False
		else:
			return self.isValid(scheduled_task_idx_arg)

		return True

	# return first available time on processor having index proc_idx
	def getFirstAvailableTime(self, proc_idx):
		if self.procs[proc_idx] == []:
			return 0

		last_sched_task_idx = self.procs[proc_idx][-1]
		return self.tasks[last_sched_task_idx].scheduled_time + \
			   self.tasks[last_sched_task_idx].duration

	# this method schedules a new task on processor proc_idx
	def scheduleTask(self, task_idx, proc_idx):
		self.tasks[task_idx].scheduled_time = self.getFirstAvailableTime(proc_idx)
		self.tasks[task_idx].scheduled_proc = proc_idx
		self.procs[proc_idx].append(task_idx)
		self.to_schedule.remove(task_idx)

	def isConsistent(self, task, proc_idx):
		curr_task_start_time = self.getFirstAvailableTime(proc_idx)

		# for each previous task that hasn't been scheduled yet, 
		# check if there is a processor on which it could be scheduled later
		# if no, the current assignment is not consistent and we shouldn't search
		# further from the current state
		for prev_task in task.prev_tasks:
			prev_task_can_be_scheduled = False

			if self.tasks[prev_task].scheduled_time != None:
				continue

			for left_proc_idx in range(len(self.procs)):
				if left_proc_idx == proc_idx:
					continue

				prev_task_end_time = self.getFirstAvailableTime(left_proc_idx) + self.tasks[prev_task].duration

				if prev_task_end_time <= curr_task_start_time:
					prev_task_can_be_scheduled = True
					break

			if not prev_task_can_be_scheduled:
				return False

		return True
