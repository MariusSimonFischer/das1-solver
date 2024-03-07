import gurobipy as gp
from gurobipy import GRB, quicksum
import time as t
import DataMappings as dict_map
import folium
from folium import plugins


def lazy_callback(model, where):
    if where == GRB.Callback.MIPSOL:
        # Extract the solution values
        x_values = model.cbGetSolution(model._vars)

        selected = gp.tuplelist(edge for edge in model._edges if x_values[edge] > 0.5)

        # Find subtours using the solution values
        subtours = find_subtour(selected)

        # If subtours are found, add lazy constraints
        if len(subtours) > 1:
            for tour in subtours:
                model.cbLazy(quicksum(model._vars[arc] for arc in tour) <= len(tour) - 1)
                model._subtours.append(tour)


# Function to find subtours in the solution
def find_subtour(used_edges):
    subtours = list()

    while len(used_edges) > 0:
        tour_nodes = {list(used_edges[0])[0], list(used_edges[0])[1]}
        tour_edges = [used_edges[0]]
        used_edges.remove(used_edges[0])

        while True:
            # next_edges = [edge for edge in used_edges if list(edge)[0] in tour_nodes or list(edge)[1] in tour_nodes]
            next_edges = [edge for edge in used_edges if list(edge)[0] in tour_nodes]

            for edge in next_edges:
                tour_nodes.update(edge)
                tour_edges.append(edge)
                used_edges.remove(edge)

            if len(next_edges) == 0:
                subtours.append(tour_edges)
                break

    return subtours


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

        # TEST
        self.u = None

        # Constraints
        self.c2 = []
        self.c3 = []
        self.flow_conservation_constraint = None
        self.no_optional_stops = None
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

    def visualize_solution(self):

        # Get the values of decision variable x after optimization
        edge_values = {edge: var.x for edge, var in self.x.items()}
        # print(edge_values)

        # Identify edges that are used in the solution (where x[edge] == 1)
        used_edges = [edge for edge, value in edge_values.items() if
                      value > 0.5]  # Considering a tolerance for binary values
        # Extract information about nodes from used edges
        used_nodes = set()
        for edge in used_edges:
            used_nodes.add(edge[0])  # Add the first node of the edge
            used_nodes.add(edge[1])  # Add the second node of the edge

        # Display information about used nodes, including their orders
        # print("Nodes used in the solution with their orders:")
        # bring used_nodes into order
        used_nodes = sorted(used_nodes, key=lambda node: node.order)
        # make used_nodes a list
        used_nodes = list(used_nodes)

        # Display information about unused nodes, including their orders
        # print("Nodes not used in the solution with their orders:")
        # bring used_nodes into order
        unused_nodes = [node for node in self.network.nodes if node not in used_nodes]
        unused_nodes = sorted(unused_nodes, key=lambda node: node.order)
        # make unused_nodes a list
        unused_nodes = list(unused_nodes)

        # Create a Folium map centered on the first compulsory stop (you can adjust this)
        map_center = (self.first_comp_stop.latitude, self.first_comp_stop.longitude)
        my_map = folium.Map(location=map_center, zoom_start=14)

        # Add markers for used nodes
        for node in used_nodes:
            popup_content = (f"Node Order: {node.order}, Segment: {node.segment_h}, "
                             f"Is Compulsory Stop: {node.is_compulsory_stop}")
            icon_color = 'green' if node.is_compulsory_stop else 'blue'
            folium.Marker(
                location=(node.latitude, node.longitude),
                popup=popup_content,
                icon=folium.Icon(color=icon_color)
            ).add_to(my_map)

        # Add markers for unused nodes
        for node in unused_nodes:
            popup_content = (f"Node Order: {node.order}, Segment: {node.segment_h}, "
                             f"Is Compulsory Stop: {node.is_compulsory_stop}")
            icon_color = 'red' if node.is_compulsory_stop else 'gray'
            folium.Marker(
                location=(node.latitude, node.longitude),
                popup=popup_content,
                icon=folium.Icon(color=icon_color)
            ).add_to(my_map)

        # Add polylines for used edges
        for edge in used_edges:
            coords = [(edge[0].latitude, edge[0].longitude), (edge[1].latitude, edge[1].longitude)]
            folium.PolyLine(
                coords,
                color='blue',
                weight=2.5,
                popup=f"Length of edge: {self.network[edge[0]][edge[1]]['weight']:.2f}",
                opacity=1
            ).add_to(my_map)

        # Display the map
        my_map.save("solution_map.html")

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

        self.flow_conservation_constraint = {
            node: self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.out_edges(node)) -
                                       gp.quicksum(self.x[arc] for arc in self.network.in_edges(node)) == 0)
            for node in self.network.nodes if node != self.first_comp_stop and node != self.last_comp_stop}

        # Case without optional stops
        ##################################################################################
        """
        self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.out_edges(self.first_comp_stop)) == 1)

        self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.in_edges(self.last_comp_stop)) == 1)

        self.flow_conservation_constraint = {
            node: self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.out_edges(node)) -
                                       gp.quicksum(self.x[arc] for arc in self.network.in_edges(node)) == 0)
            for node in self.network.nodes if node != self.first_comp_stop and node != self.last_comp_stop
                                              and node.is_compulsory_stop}

        self.no_optional_stops = {
            node: self.model.addConstr(gp.quicksum(self.x[arc] for arc in self.network.in_edges(node)) == 0)
            for node in self.network.nodes if not node.is_compulsory_stop}
        """
        ##################################################################################


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
        self.model._vars = self.x
        self.model._nodes = self.network.nodes
        self.model._edges = self.network.edges
        self.model._subtours = list()
        # self.model.Params.LogToConsole = 0
        self.model.Params.lazyConstraints = 1

        # Optimize the model with lazy constraints
        self.model.optimize(lazy_callback)  # lazy_callback

    def several_instances(self):
        # Check if the model is solved to optimality
        if self.model.status == GRB.OPTIMAL:
            # Get values of served and unserved requests
            served_requests = [r for r in self.R if self.y[r].X > 0.5]
            unserved_requests = [r for r in self.R if self.y[r].X <= 0.5]

            num_served_requests = len(served_requests)
            num_unserved_requests = len(unserved_requests)
            # print(f"Number of served requests: {num_served_requests}")
            # print(f"Number of unserved requests: {num_unserved_requests}")

            # Get the total driven distance after optimization
            total_driven_distance = sum(self.network[arc[0]][arc[1]]['weight'] * self.x[arc].X
                                        for arc in self.network.edges())
            # print(f"Total driven distance: {total_driven_distance}")

            # Get the respective arrival time at each compulsory stop reflected by the variable t
            arrival_time_at_comp_stops = [self.t[h].X for h in range(len(self.time_bounds))]
            # print(f"Arrival time at each compulsory stop: {arrival_time_at_comp_stops}")

            # Get total travel time
            total_travel_time = (arrival_time_at_comp_stops[len(arrival_time_at_comp_stops) - 1] -
                                 arrival_time_at_comp_stops[0])
            # print(f"Total travel time: {total_travel_time}")

            # Get the values of decision variable x after optimization
            edge_values = {edge: var.x for edge, var in self.x.items()}
            # print(edge_values)

            # Identify edges that are used in the solution (where x[edge] == 1)
            used_edges = [edge for edge, value in edge_values.items() if
                          value > 0.5]  # Considering a tolerance for binary values
            # print("Edges used in the solution:")
            # print(used_edges)

            # Extract information about nodes from used edges
            used_nodes = set()
            for edge in used_edges:
                used_nodes.add(edge[0])  # Add the first node of the edge
                used_nodes.add(edge[1])  # Add the second node of the edge

            # Display information about used nodes, including their orders
            print("Nodes used in the solution with their orders:")
            # bring used_nodes into order
            used_nodes = sorted(used_nodes, key=lambda node: node.order)

            for node in used_nodes:
                print(f"Is Compulsory Stop: {node.is_compulsory_stop},"
                      f"Is Origin: {node.is_origin},"
                      f"Is Destination: {node.is_destination},"
                      f"Node Order: {node.order}, "
                      f"Latitude: {node.latitude}, "
                      f"Longitude: {node.longitude}"
                      f"Segment: {node.segment_h}"
                      )

            # make used_nodes a list
            used_nodes = list(used_nodes)

            # Display information about unused nodes, including their orders
            print("Nodes not used in the solution with their orders:")
            # bring used_nodes into order
            unused_nodes = [node for node in self.network.nodes if node not in used_nodes]
            unused_nodes = sorted(unused_nodes, key=lambda node: node.order)

            for node in unused_nodes:
                print(f"Is Compulsory Stop: {node.is_compulsory_stop},"
                      f"Is Origin: {node.is_origin},"
                      f"Is Destination: {node.is_destination},"
                      f"Node Order: {node.order}, "
                      f"Latitude: {node.latitude}, "
                      f"Longitude: {node.longitude}"
                      f"Segment: {node.segment_h}"
                      )

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

            num_segments = len(self.segments)
            num_requests = len(self.request_pairs)
            num_opt_stops = len(dict_map.route_nodes) - len(dict_map.compulsory_stops)
            num_opt_stops_visited = len(used_nodes) - len(dict_map.compulsory_stops)
            num_opt_stops_not_visited = ((len(dict_map.route_nodes) - len(dict_map.compulsory_stops)) - (
                        len(used_nodes) - len(dict_map.compulsory_stops)))

            # ----------Testing-----------------------------------------------------------------------------------------

            print("Testing:")
            print(f"Result: {self.model.objVal}")
            print(f"Number of segments: {len(self.segments)}")
            print(f"Number of requests: {len(self.request_pairs)}")
            print(f"Number of served requests: {num_served_requests}")
            print(f"Number of unserved requests: {num_unserved_requests}")
            print(f"Amount of stops: {len(dict_map.route_nodes)}")
            print(f"Amount compulsory stops: {len(dict_map.compulsory_stops)}")
            print(f"Amount optional stops: {len(dict_map.route_nodes) - len(dict_map.compulsory_stops)}")
            print(f"Amount of optional stops visited: {len(used_nodes) - len(dict_map.compulsory_stops)}")
            print(
                f"Amount of optional stops not visited: {((len(dict_map.route_nodes) - len(dict_map.compulsory_stops)) - (len(used_nodes) - len(dict_map.compulsory_stops)))}")

            return (num_segments, num_requests, served_requests, unserved_requests, used_nodes,
                    unused_nodes, total_driven_distance, num_opt_stops, num_opt_stops_visited,
                    num_opt_stops_not_visited,
                    total_travel_time, arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val)

        else:
            print("Optimization did not converge to an optimal solution.")
            return None

    def main(self):
        """
        Main function to call the other functions
        :return:
        """

        # Build the model
        self.build_model()

        # Optimize the model
        self.optimizer()

        # Visualize the solution
        self.visualize_solution()

        result = self.several_instances()

        return result
