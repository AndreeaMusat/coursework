import sys
import pickle
import itertools
from copy import deepcopy

# this is an instance of a predicate
class Atom(object):
	
	def __init__(self, name, variables, values, is_static):
		if len(variables) != len(values):
			print("Error, could not create atom with vars = " + str(variables) + \
				" and vals = " + str(values))
		self.name = name
		self.variables = variables
		self.values = values
		self.is_static = is_static

	def __eq__(self, other):
		if isinstance(other, Atom):
			return self.name == other.name and \
				   len(self.variables) == len(other.variables) and \
				   self.values == other.values and \
				   self.is_static == other.is_static
		else:
			return False

	def get_variables(self):
		return self.variables

	def get_values(self):
		return self.values

	def __hash__(self):
		return hash(self.name, len(self.variables), self.values, self.is_static)

	def __str__(self):
		s = self.name + "("
		for i in range(len(self.variables)):
			s += self.variables[i] + " = " + str(self.values[i])
			if i != len(self.variables) - 1:
				s += ", "
		s += ")"
		return s

# this is a logic predicate; it has a name, 
# a list of variables and a domain for every
# variable 
class Predicate(object):

	def __init__(self, name, variables, domains, is_static):

		if len(variables) != len(domains):
			print("Error creating pred " + name + "with vars = " + \
				str(variables) + " and domains = " + str(domains))
		self.name = name
		self.variables = variables
		self.domains = domains
		self.is_static = is_static

	# variables[i] has value values[i]
	def get_instance(self, variables, values):
		my_values = []
		for variable in self.variables:
			if variable not in variables:
				print("error - variable not found in variables argument")
			else:
				my_values.append(values[variables.index(variable)])
		return Atom(self.name, self.variables, my_values, self.is_static)

	# return a dict: var name -> domain
	def get_variables(self):
		pred_vars = {}
		for i in range(len(self.variables)):
			pred_vars[self.variables[i]] = self.domains[i]

		return pred_vars

	# string representation of current predicate
	def __str__(self):
		res = self.name + "("
		for i in range(len(self.variables)):
			res += self.variables[i]
			if i != len(self.variables) - 1:
				res += ", "
		res += ")"
		return res


# this is an action = instantiated operator
class Action(object):

	# build an action based on a predicate and a substitution
	def __init__(self, name, variables, values, main_vars):
		self.pos_preconds = []
		self.neg_preconds = []
		self.pos_effects = []
		self.neg_effects = []

		self.name = name
		self.variables = variables
		self.values = values

		self.main_variables = main_vars

	def add_pos_preconds(self, preconds_list):
		for precond in preconds_list:
			self.pos_preconds.append(precond.get_instance(self.variables, self.values))

	def add_neg_preconds(self, preconds_list):
		for precond in preconds_list:
			self.neg_preconds.append(precond.get_instance(self.variables, self.values))

	def add_pos_effects(self, effects_list):
		for effect in effects_list:
			self.pos_effects.append(effect.get_instance(self.variables, self.values))

	def add_neg_effects(self, effects_list):
		for effect in effects_list:
			self.neg_effects.append(effect.get_instance(self.variables, self.values))

	def add_all_conds(self, pos_preconds, neg_preconds, pos_effects, neg_effects):
		self.add_pos_preconds(pos_preconds)
		self.add_neg_preconds(neg_preconds)
		self.add_pos_effects(pos_effects)
		self.add_neg_effects(neg_effects)

	# return all predicates in this action (preconds + effects)
	def get_all_preds(self):
		all_preds = []
		all_preds += self.pos_preconds
		all_preds += self.neg_preconds
		all_preds += self.pos_effects
		all_preds += self.neg_effects
		return all_preds

	# if an action has some effect which is in both positive and negative effects, 
	# then the action is not valid
	def is_valid(self, scenario_preds):
		if self.name == "fly":
			start_cell_var_idx = self.variables.index("startCell")
			end_cell_var_idx = self.variables.index("endCell")
			if self.values[start_cell_var_idx] == self.values[end_cell_var_idx]:
				return False
			
		# for every +/- precondition, if the predicate is static and has > 1 variable
		# and it is not present in our scenario, then discard it
		for pos_precond in self.pos_preconds:
			if pos_precond.is_static == True and \
			   len(pos_precond.variables) > 1 and \
			   pos_precond not in scenario_preds:
				return False

		for neg_precond in self.neg_preconds:
			if neg_precond.is_static == True and \
			   len(neg_precond.variables) > 1 and \
			   neg_precond not in scenario_preds:
				return False

		return True

	def __str__(self):
		s = self.name + "("
		for i in range(len(self.main_variables)):
			var_idx = self.variables.index(self.main_variables[i])
			s += str(self.values[var_idx]) 
			if i != len(self.main_variables) - 1:
				s += ","
		s += ")"
		if self.name == "load":
			end_cell_var_idx = self.variables.index("endCell")
			client_cell_var_idx = self.variables.index("client_cell")
			s += ", " + "fly" + "(" + str(self.values[end_cell_var_idx]) + \
				"," + str(self.values[client_cell_var_idx]) + ")"
		return s

	def __repr__(self):
		return self.__str__()

# this is a strips operator; it has a name, a list
# of variables, a list of domains for every variable
# 2 lists of preconditions (+ and -) and 2 lists of effects (+ and -)
class Operator(object):

	# todo: do i need some restrictions on some variables ?? -> i think no
	def __init__(self, name, variables, domains):
		self.pos_preconds = []
		self.neg_preconds = []
		self.pos_effects = []
		self.neg_effects = []

		self.name = name
		self.variables = variables
		self.domains = domains

	def add_pos_precond(self, precond_pred):
		self.pos_preconds.append(precond_pred)

	def add_neg_precond(self, precond_pred):
		self.neg_preconds.append(precond_pred)

	def add_pos_effect(self, effect_pred):
		self.pos_effects.append(effect_pred)

	def add_neg_effect(self, effect_pred):
		self.neg_effects.append(effect_pred)

	# collect all the variables that appear in the conditions &
	# effects of this operator and their domain
	# return a dictionary var name -> (variable, domain)
	def get_all_variables(self):
		all_variables = {}

		all_preds = list(set().union(self.pos_preconds, self.neg_preconds))
		all_preds = list(set().union(all_preds, self.pos_effects, self.neg_effects))

		for pred in all_preds:
			all_variables.update(pred.get_variables())

		return all_variables

	def get_valid_instances(self, scenario_preds):
		actions = []

		# use itertools to create all the possible combinations of values
		all_variables = self.get_all_variables()
		just_vars = list(all_variables)
		just_domains = all_variables.values()

		all_possible_combs_values = list(itertools.product(*just_domains))
		
		substs = []
		for vals in all_possible_combs_values:
			new_subst = {}
			for i in range(len(just_vars)):
				new_subst[just_vars[i]] = vals[i]
			substs.append(new_subst)

		# now i have to make an action with every substitution
		# and only keep de actions that are valid (an action that has a static predicate
		# with more than one variable and that predicate is not given as true is not valid)		
		for subst in substs:
			new_action = Action(self.name, subst.keys(), subst.values(), self.variables)
			new_action.add_all_conds(self.pos_preconds, self.neg_preconds, self.pos_effects, self.neg_effects)
			if new_action.is_valid(scenario_preds):
				actions.append(new_action)

		return actions

# this is a state; it has a set of predicates that are true
# and all the others not present are considered false
class State(object):

	def __init__(self):
		self.pos_preds = []

	# add a predicate to the list of true predicates in the state
	def add_pos_pred(self, pos_pred):
		for pred in self.pos_preds:
			if pred == pos_pred:
				return
		self.pos_preds.append(pos_pred)

	def remove_pos_pred(self, pos_pred):
		for pred in self.pos_preds:
			if pred == pos_pred:    # hopefully this uses the overriden operator
				self.pos_preds.remove(pred)
				return

	def get_state_vars_dict(self):
		state_vars = {}
		for atom in self.pos_preds:
			pred_vars = atom.get_variables()
			pred_vals = atom.get_values()

			for i in range(len(pred_vars)):
				if pred_vars[i] in state_vars and state_vars[pred_vars[i]] != pred_vals[i]:
				   	for p in self.pos_preds:
				   		print(str(p) + "\n")
				   	return None
				if pred_vars[i] not in state_vars:
					state_vars[pred_vars[i]] = pred_vals[i]
		return state_vars

	# get applicable actions in current state
	# operator is a dictionary operator_name => operator object
	def get_applicable_actions(self, operators, scenario_preds, last_action_name):

		# state vars = dictionary with variables that are in current
		# state mapped to their values
		state_vars = self.get_state_vars_dict()
		if state_vars == None:
			return []

		# for every operator in operators, get all the possible actions
		possible_actions = []
		
		actions_list = ["deliver", "load", "fly"]
		for operator_key in actions_list:
			new_actions = operators[operator_key].get_valid_instances(scenario_preds)

			for action in new_actions:
				ok = True

				# check that all positive effects of current action are in curr state
				for pos_eff in action.pos_effects:
					if pos_eff.is_static == True:
						continue
					if pos_eff not in self.pos_preds:
						# print("Pos eff " + str(pos_eff) + " is not in state")
						ok = False
						break

				if not ok:
					# print("not all + effects are there.. :( bye")
					continue

				# check if no negative effect of the action is in state
				neg_effects_in_state = [eff for eff in action.neg_effects if eff in self.pos_preds]
				neg_effects_in_state = [eff for eff in neg_effects_in_state if eff.is_static == False]
				if neg_effects_in_state != []:
					continue

				# now check if variables having the same name (in curr state and 
				# in curr action) also have the same value
				ok = True
				all_preds_in_action = action.get_all_preds()
				for pred in all_preds_in_action:
					if not ok:
						break

					pred_vars = pred.get_variables()
					pred_vals = pred.get_values()

					for i in range(len(pred_vars)):
						if pred_vars[i] in state_vars and \
						   state_vars[pred_vars[i]] != pred_vals[i]:
						   ok = False
						   break

				if ok:
					possible_actions.append(action)

		return possible_actions

	# choose one action
	def choose_action(self, all_actions):
		return all_actions[0]

	# prev_state = state - effects(action) + precond(action)
	def inverse_transition(self, action):
		new_state = self

		for pos_effect in action.pos_effects:
			new_state.remove_pos_pred(pos_effect)

		for neg_effect in action.neg_effects:
			new_state.add_pos_pred(neg_effect)

		for pos_precond in action.pos_preconds:
			new_state.add_pos_pred(pos_precond)

		for neg_precond in action.neg_preconds:
			new_state.remove_pos_pred(neg_precond)

		return new_state

	def __hash__(self):
		return hash(self.pos_preds)

	# return True if goal_states contains at least 
	# all the true predicates in self state
	def satisfies(self, goal_state):

		for pred in self.pos_preds:
			if pred.is_static == False and pred not in goal_state.pos_preds:
				return False
		return True
