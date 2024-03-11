# Import the Gurobi Python library.
import gurobipy as gp
from gurobipy import GRB


# Example data
# Define the number of segments and their parameters
n_segments = 4  # Number of segments
a_t = [0, 10, 20, 30]  # earliest Start time for segments
b_t = [0, 12, 22, 32]  # latest Start time for segments

travel_time_matrix = [[[10, 20, 5], [10, 1, 4], [1, 2, 2], [1, 20, 5], [2, 20, 3], [10, 2, 3]],
                      [[20, 30, 5], [20, 3, 5], [3, 30, 6]],
                      [[30, 40, 5], [30, 5, 4], [30, 6, 3], [5, 6, 2], [5, 40, 6], [6, 40, 3]],
                      [[40, 50, 5], [40, 7, 5], [7, 50, 4]]]
# travel time matrix for each arc [i, j, travel time] (compulsory nodes are 1-5 *10, optional nodes are 1-n)


# Define the number of requests and their parameters
r_requests = 3  # Number of requests
requests = [(1, 3), (1, 3), (2, 4)]  # (s(r), d(r)) pairs (start segment, destination segment)
u_benefit_of_r = [10, 8, 9]  # Benefit for each request

# Define the cost for each arc [i,j,cost]
cost_matrix = [[[10, 20, 5], [10, 1, 4], [1, 2, 2], [1, 20, 5], [2, 20, 3], [10, 2, 3]],
               [[20, 30, 5], [20, 3, 5], [3, 30, 6]],
               [[30, 40, 5], [30, 5, 4], [30, 6, 3], [5, 6, 2], [5, 40, 6], [6, 40, 3]],
               [[40, 50, 5], [40, 7, 5], [7, 50, 4]]]

# Create a Gurobi model
# Create an empty optimization model with the name "DAs1."
model = gp.Model("DAs1")

# Decision variables
x = {}
y = {}
t = {}


# Create dictionaries to hold decision variables.
# Define and create binary decision variables for x, y, and t.
for h in range(n_segments):
    num_arcs_in_segment_n = len(travel_time_matrix[h])
    for i in range(num_arcs_in_segment_n):
        for j in range(num_arcs_in_segment_n):
            x[i, j, h] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}_{h}')
    for r in range(r_requests):
        y[r] = model.addVar(vtype=GRB.BINARY, name=f'y_{r}')
    t[h] = model.addVar(lb=a_t[h], ub=b_t[h], name=f't_{h}')


# Update the model to incorporate the new variables.
model.update()

# Objective function
obj = (gp.quicksum(u_benefit_of_r[r] * y[r] for r in range(r_requests)) - gp.quicksum(
    cost_matrix[h][i][j] * x[i, j, h] for h in range(n_segments) for i in range(n_segments + 1) for j in range(n_segments + 1)))

# Define and set the objective function to maximize the profit.
model.setObjective(obj, GRB.MAXIMIZE)

# Define Constraints
for h in range(n_segments):
    model.addConstr(gp.quicksum(x[i, j, h] for (i, j) in [(p, q) for p in range(n_segments + 1) for q in range(n_segments + 1)]) == 1)

# Add constraints to ensure exactly one arc is selected in each segment.

for h in range(n - 1):
    model.addConstr(
        t[h] + gp.quicksum(tau[h][i][j] * x[i, j, h] for i in range(n + 1) for j in range(n + 1)) <= t[h + 1])

# Add constraints to ensure time feasibility.

for r in range(R):
    for h in range(n):
        model.addConstr(y[r] <= gp.quicksum(
            x[i, j, h] for i in range(n + 1) for j in range(n + 1) if i == requests[r][0] or j == requests[r][1]))

# Add constraints to relate request satisfaction to arc selection.

model.optimize()

# Solve the optimization model.

# Print the solution
if model.status == GRB.OPTIMAL:
    print("Optimal solution found")
    for h in range(n):
        print(f"Segment {h + 1}:")
        for i in range(n + 1):
            for j in range(n + 1):
                if x[i, j, h].X > 0.5:
                    print(f"Arc ({i}, {j}) is selected in Segment {h}")
        print(f"Start time: {t[h].X}")
    print("Selected Requests:")
    for r in range(R):
        if y[r].X > 0.5:
            print(f"Request {r + 1} is satisfied")
    print(f"Total Profit: {model.objVal}")

else:
    print("No optimal solution found")

# Print the solution if an optimal solution is found, including selected arcs, start times, satisfied requests, and total profit. If no optimal solution is found, indicate that no solution is found.
