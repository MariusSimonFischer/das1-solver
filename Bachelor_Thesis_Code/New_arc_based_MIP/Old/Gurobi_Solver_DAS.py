import gurobipy as gp
from gurobipy import GRB
import time as t
import DataMappings as dict_map


class DASOptimizer:
    def __init__(self, benefit_u, network, request_pairs, time_bounds, segments, delta_origin,
                 delta_destination):
        """
        :param benefit_u: benefit for each request
        :param network: networkx graph
        :param request_pairs: list of all request pairs (of the form: request_pairs =
        [{'origin': {'latitude': 12.567890, 'longitude':4.456784},
        'destination': {'latitude': 12.567890, 'longitude':4.456784}}, ... ]
        :param time_bounds: time bounds for all nodes (of the form: [{'a': 0, 'b': 0}, {'a': 1.4567, 'b': 2.3456}, ...])
        :param segments: number of segments as [] (starting at 1)
        :param delta_origin: dictionary containing a key for every request, and a list of all nodes (1 or 0) as
        values, indicating whether the request is equal the node
        :param delta_destination: dictionary containing a key for every request, and a list of all nodes (1 or 0)
        as values, indicating whether the request is equal the node
        """
        self.benefit_u = benefit_u
        self.segments = segments
        self.network = network
        self.request_pairs = request_pairs
        self.time_bounds = time_bounds
        self.delta_origin = delta_origin
        self.delta_destination = delta_destination

        # Model
        self.model = None

        # Variables
        self.x = None
        self.y = None
        self.t = None

        # Constraints
        self.c2 = []
        self.c3 = []
        self.flow_conservation_constraint = None
        self.c5 = None
        self.c6 = None

        # first and last compulsory stop

        for node in self.network.nodes:
            if node.is_compulsory_stop and node.is_origin:
                self.first_comp_stop = node

        for node in self.network.nodes:
            if node.is_compulsory_stop and node.is_destination:
                self.last_comp_stop = node

        # range of request set
        self.R = range(len(request_pairs))

        # start time building
        self.start_time = None

        # end time building
        self.end_time = None

    def build_model(self):
        """
        Function to build the model for the S-DAS problem
        :return:
        """
        self.start_time = t.time()

        self.model = gp.Model("S-DAS-MIP")

        # Variables & Objective Function (& Constraint 7)
        self.x = {arc: self.model.addVar(vtype=GRB.BINARY)  # obj=-self.network[arc[0]][arc[1]]['weight']
                  for arc in self.network.edges()}
        self.y = {r: self.model.addVar(vtype=GRB.BINARY) for r in self.R}  # obj=self.benefit_u
        self.t = {h: self.model.addVar(vtype=GRB.CONTINUOUS, lb=self.time_bounds[h]['a'], ub=self.time_bounds[h]['b'])
                  for h in range(len(self.time_bounds))}

        # Objective Function
        self.model.setObjective(gp.quicksum(self.benefit_u * self.y[r] for r in self.R) -
                                gp.quicksum(self.network[arc[0]][arc[1]]['weight'] * self.x[arc]
                                            for arc in self.network.edges()),
                                GRB.MAXIMIZE)

        # Constraints (6) ensures that the journey completion time does
        # not exceed the maximum allowed time
        self.c6 = {self.model.addConstr(
            self.t[len(self.time_bounds) - 2] + gp.quicksum(self.network[arc[0]][arc[1]]['time'] * self.x[arc]
                                                            for arc in self.network.edges
                                                            if self.network[arc[0]][arc[1]]['segment']
                                                            == self.segments[len(self.segments) - 1]) <=
            self.time_bounds[len(self.time_bounds) - 1]['b'],
            name=f"Journey_Completion")}

        # Constraints (5)
        # travel time constraints
        for h in range(len(self.time_bounds) - 1):
            self.model.addConstr(self.t[h] + gp.quicksum(self.network[arc[0]][arc[1]]['time'] * self.x[arc]
                                                         for arc in self.network.edges
                                                         if self.network[arc[0]][arc[1]]['segment'] == h + 1) <=
                                 self.t[h + 1],
                                 name=f"Time_Progression_{h}")

        # Constraints (4)
        # represent flow conservation at each node in the network
        self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.out_edges(self.first_comp_stop)) == 1)

        self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.in_edges(self.last_comp_stop)) == 1)

        # make sure that each compulsory stop is visited exactly once
        for node in self.network.nodes:
            if node.is_compulsory_stop and node != self.first_comp_stop and node != self.last_comp_stop:
                self.model.addConstr(
                    gp.quicksum(self.x[arc] for arc in self.network.out_edges(node)) == 1)
                self.model.addConstr(
                    gp.quicksum(self.x[arc] for arc in self.network.in_edges(node)) == 1)

        self.flow_conservation_constraint = {
            node: self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.out_edges(node)) -
                                       gp.quicksum(self.x[arc] for arc in self.network.in_edges(node)) == 0)
            for node in self.network.nodes if node != self.first_comp_stop and node != self.last_comp_stop}

        # The constraints (2) and (3) ensure that first, the served requests within the tour and the chosen
        # arcs are linked, and second for each request, boarding and alighting stops are coupled,
        # ensuring that the pick-up and drop-off locations s(r) and d(r) of request r are reachable in
        # the network if the request is satisfied.
        # Constraints (3)
        for r in self.R:
            constraint_c3 = {self.model.addConstr(self.y[r] <=
                                                  gp.quicksum(self.x[arc] * self.delta_origin[r][arc[0].order]
                                                              for arc in self.network.edges()))}
            self.c3.append(constraint_c3)

        # Constraints (2)
        for r in self.R:
            constraint_c2 = {self.model.addConstr(self.y[r] <=
                                                  gp.quicksum(
                                                      self.x[arc] * self.delta_destination[r][arc[1].order]
                                                      for arc in self.network.edges()))}
            self.c2.append(constraint_c2)

        self.end_time = t.time()

    def optimizer(self):
        """
        Function to optimize the model
        :return:
        """
        self.model.optimize()

        # Get number of served and unserved requests
        if self.model.status == GRB.OPTIMAL:
            # Get values of served requests after optimization
            # Get values of served and unserved requests
            served_requests = [r for r in self.R if self.y[r].X > 0.5]
            unserved_requests = [r for r in self.R if self.y[r].X <= 0.5]

            num_served_requests = len(served_requests)
            num_unserved_requests = len(unserved_requests)

            # print(f"Number of served requests: {num_served_requests}")
            # print(f"Number of unserved requests: {num_unserved_requests}")

            # Get the total driven distance after optimization
            # Calculate total driven distance
            total_driven_distance = sum(self.network[arc[0]][arc[1]]['weight'] * self.x[arc].X
                                        for arc in self.network.edges())

            # print(f"Total driven distance: {total_driven_distance}")

            # Get the respective arrival time at each compulsory stop reflected by the variable t
            # Calculate arrival time at each compulsory stop
            arrival_time_at_comp_stops = [self.t[h].X for h in range(len(self.time_bounds))]
            # print(f"Arrival time at each compulsory stop: {arrival_time_at_comp_stops}")

            # Get total travel time
            total_travel_time = arrival_time_at_comp_stops[len(arrival_time_at_comp_stops) - 1] - \
                                arrival_time_at_comp_stops[0]
            # print(f"Total travel time: {total_travel_time}")

            # Show more information:
            # print solution
            # print('Obj: %g' % self.model.objVal)
            # Get the values of decision variable x after optimization
            edge_values = {edge: var.x for edge, var in self.x.items()}
            # print(edge_values)

            # Identify edges that are used in the solution (where x[edge] == 1)
            used_edges = [edge for edge, value in edge_values.items() if
                          value > 0.5]  # Considering a tolerance for binary values

            # Display the edges used in the solution
            # print("Edges used in the solution:")
            # print(used_edges)

            # Extract information about nodes from used edges
            used_nodes = set()
            for edge in used_edges:
                used_nodes.add(edge[0])  # Add the first node of the edge
                used_nodes.add(edge[1])  # Add the second node of the edge

            # Display information about used nodes, including their orders
            # print("Nodes used in the solution with their orders:")
            # bring used_nodes into order
            used_nodes = sorted(used_nodes, key=lambda node: node.order)
            """"
            for node in used_nodes:
                print(f"Is Compulsory Stop: {node.is_compulsory_stop},"
                      f"Is Origin: {node.is_origin},"
                      f"Is Destination: {node.is_destination},"
                      f"Node Order: {node.order}, "
                      f"Latitude: {node.latitude}, "
                      f"Longitude: {node.longitude}"
                      f"Segment: {node.segment_h}"
                      )
            """
            # make used_nodes a list
            used_nodes = list(used_nodes)

            # Display information about unused nodes, including their orders
            # print("Nodes not used in the solution with their orders:")
            # bring used_nodes into order
            unused_nodes = [node for node in self.network.nodes if node not in used_nodes]
            unused_nodes = sorted(unused_nodes, key=lambda node: node.order)
            """
            for node in unused_nodes:
                print(f"Is Compulsory Stop: {node.is_compulsory_stop},"
                      f"Is Origin: {node.is_origin},"
                      f"Is Destination: {node.is_destination},"
                      f"Node Order: {node.order}, "
                      f"Latitude: {node.latitude}, "
                      f"Longitude: {node.longitude}"
                      f"Segment: {node.segment_h}"
                      )
            """
            # make unused_nodes a list
            unused_nodes = list(unused_nodes)

            # Find solve time
            solve_time = self.model.Runtime

            # Find build time
            build_time = self.end_time - self.start_time

            # Find optimality gap
            opt_gap = self.model.MIPGap

            # Get solution of the model
            obj_val = self.model.objVal
            print(obj_val)

            # ----------Testing-----------------------------------------------------------------------------------------
            print("Testing:")
            print(f"Number of requests: {len(self.request_pairs)}")
            print(f"Number of served requests: {num_served_requests}")
            print(f"Number of unserved requests: {num_unserved_requests}")
            print(f"Amount of stops: {len(dict_map.route_nodes)}")
            print(f"Amount compulsory stops: {len(dict_map.compulsory_stops)}")
            print(f"Amount optional stops: {len(dict_map.route_nodes) - len(dict_map.compulsory_stops)}")



            return (served_requests, unserved_requests, used_nodes, unused_nodes, total_driven_distance,
                    total_travel_time, arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val)

        else:
            print("Optimization did not converge to an optimal solution.")

    def main(self):
        """
        Main function to call the other functions
        :return:
        """
        self.build_model()
        result = self.optimizer()

        return result
