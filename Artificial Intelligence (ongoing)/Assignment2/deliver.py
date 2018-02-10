from util import *

preds = None
ops = None
scenario_atoms = None
initial_pos = None

goals = None
initial_state = None

cell_domain = None
client_cell_domain = None
warehouse_cell_domain = None
order_id_domain = None
product_id_domain = None

def get_domains(scenario):
	global cell_domain, client_cell_domain
	global warehouse_cell_domain
	global order_id_domain, product_id_domain
	global initial_pos

	client_cell_domain = scenario["clients"]
	warehouse_cell_domain = scenario["warehouses"]
	order_id_domain = range(len(scenario["orders"]))
	product_id_domain = range(len(scenario["available_products"]))
	cell_domain = warehouse_cell_domain + client_cell_domain + [scenario["initial_position"]]
	initial_pos = scenario["initial_position"]

def create_scenario_atoms(scenario):
	global scenario_atoms

	scenario_atoms = []
	for entry in scenario["available_products"]:
		scenario_atoms.append(Atom("hasProduct", ["warehouse_cell", "product_id"], \
			[entry[0], entry[1]], True))

	order_id = 0
	for entry in scenario["orders"]:
		scenario_atoms.append(Atom("order", ["client_cell", "product_id", "order_id"], \
			[entry[0], entry[1], order_id], True))
		order_id += 1

	global initial_state

	initial_state = State()
	initial_state.add_pos_pred(Atom("empty", [], [], False))
	for warehouse_cell in warehouse_cell_domain:
		initial_state.add_pos_pred(Atom("dronePos", ["startCell"], [warehouse_cell], False))

	global goals
	goals = []
	for i in range(len(scenario["orders"])):
		new_goal_state = State()
		new_goal_state.add_pos_pred(Atom("satisfied", ["order_id"], [i], False))
		new_goal_state.add_pos_pred(Atom("dronePos", ["endCell"], [scenario["orders"][i][0]], False))
		new_goal_state.add_pos_pred(Atom("empty", [], [], False))
		goals.append(new_goal_state)
	
# name of operator => operator object
def create_operators():
	global ops
	ops = {}

	# deliver operator -> deliver product_id to a customer who ordered it
	ops["deliver"] = Operator("deliver", ["product_id"], [product_id_domain])
	# precond 1: the drone should be carying the product
	ops["deliver"].add_pos_precond(Predicate("carries", ["product_id"], [product_id_domain], False))
	# precond 2: there should be a client who ordered the product
	ops["deliver"].add_pos_precond(Predicate("client", ["startCell"], [client_cell_domain], True))
	ops["deliver"].add_pos_precond(Predicate("order", ["startCell", "product_id", "order_id"], \
		[client_cell_domain, product_id_domain, order_id_domain], True))
	# precond 3: the drone should not be empty
	ops["deliver"].add_neg_precond(Predicate("empty", [], [], False))
	# precond 4: the order should not be satisfied
	ops["deliver"].add_neg_precond(Predicate("satisfied", ["order_id"], [order_id_domain], False))

	# postcond 1: the drone arrives at the client's position
	ops["deliver"].add_pos_effect(Predicate("dronePos", ["startCell"], [client_cell_domain], False))
	# postcond 2: the drone is empty
	ops["deliver"].add_pos_effect(Predicate("empty", [], [], False))
	# postcond 3: the order is now satisfied
	ops["deliver"].add_pos_effect(Predicate("satisfied", ["order_id"], [order_id_domain], False))
	
	# postcond 4: the drone is not carying the product anymore
	ops["deliver"].add_neg_effect(Predicate("carries", ["product_id"], [product_id_domain], False))

	# load operator: put a product in the drone
	ops["load"] = Operator("load", ["product_id"], [product_id_domain])
	# precond 1: the drone should be in cell
	ops["load"].add_pos_precond(Predicate("dronePos", ["endCell"], [warehouse_cell_domain], False))
	# precond 2: cell should also be the position of a warehouse
	ops["load"].add_pos_precond(Predicate("warehouse", ["endCell"], [warehouse_cell_domain], True))
	# precond 3: the drone should be empty
	ops["load"].add_pos_precond(Predicate("empty", [], [], False))
	# precond 4: the warehouse should have the product I am looking for
	ops["load"].add_pos_precond(Predicate("hasProduct", ["endCell", "product_id"], \
		[warehouse_cell_domain, product_id_domain], True))
	# precond 5 & 6: there should be a client who ordered that product
	ops["load"].add_pos_precond(Predicate("client", ["client_cell"], [client_cell_domain], True))
	ops["load"].add_pos_precond(Predicate("order", ["client_cell", "product_id", "order_id"], \
		[client_cell_domain, product_id_domain, order_id_domain], True))
	# postcond 1: the drone now carries the product with id product_id
	ops["load"].add_pos_effect(Predicate("carries", ["product_id"], [product_id_domain], False))
	# postcond 2: the drone is not empty anymore
	ops["load"].add_neg_effect(Predicate("empty", [], [], False))

	# fly operator -> go from startCell to endCell
	ops["fly"] = Operator("fly", ["startCell", "endCell"], [[cell_domain]] * 2)
	# precond 1: the drone should be in startCell
	ops["fly"].add_pos_precond(Predicate("dronePos", ["startCell"], [cell_domain], False))
	# postcond 1: the drone should move to endCell
	ops["fly"].add_pos_effect(Predicate("dronePos", ["endCell"], [cell_domain], False))
	# postcond 2: the drone should change its position (startCell != endCell)
	ops["fly"].add_neg_effect(Predicate("dronePos", ["startCell"], [cell_domain], False)) # is dis ok ?

# strips backward planning algorithm
def backward_search_subgoal(goal_state):

	plan = []
	subgoal = goal_state

	while True:
		if subgoal.satisfies(initial_state):
			return plan

		if len(plan) != 0:
			applicable_actions = subgoal.get_applicable_actions(ops, scenario_atoms, plan[-1].name)
		else:
			applicable_actions = subgoal.get_applicable_actions(ops, scenario_atoms, None)
		
		if applicable_actions == []:
			return None

		action = subgoal.choose_action(applicable_actions)
		subgoal = subgoal.inverse_transition(action)
		plan = [action] + plan

def merge_plans(subplans):
	start_pos = initial_pos
	final_plan = []
	for i in range(len(subplans)):
		end_pos_var_idx = subplans[i][0].variables.index("endCell")
		end_pos = subplans[i][0].values[end_pos_var_idx]
		if i != 0:
			start_pos_var_idx = subplans[i - 1][-1].variables.index("startCell")
			start_pos = subplans[i - 1][-1].values[start_pos_var_idx]

		fly_action = Action(ops["fly"].name, ops["fly"].variables, [start_pos, end_pos], ops["fly"].variables)
		fly_action.add_all_conds(ops["fly"].pos_preconds, ops["fly"].neg_preconds, \
			ops["fly"].pos_effects, ops["fly"].neg_effects)
		final_plan.append(fly_action)
		final_plan += subplans[i]

	return final_plan

def make_plan(scenario):
	get_domains(scenario)
	create_scenario_atoms(scenario)	
	create_operators()
	subplans = []
	for subgoal in goals:
		subplans.append(backward_search_subgoal(subgoal))
	return merge_plans(subplans)

def main(args):
    scenario = pickle.load(open('Tests/example.pkl'))
    plan = make_plan(scenario)
    if plan is None:
    	print("None")
    else:
    	print(str(plan))

if __name__ == '__main__':
    main(sys.argv)
