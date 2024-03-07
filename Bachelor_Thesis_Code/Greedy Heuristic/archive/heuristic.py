import time as t


class GreedyHeuristic:
    def __init__(self, benefit_u, segments, request_pairs, compulsory_stops, time_bounds, distance_matrix,
                 time_matrix, route_nodes):
        self.benefit_u = benefit_u
        self.segments = segments
        self.request_pairs = request_pairs
        self.compulsory_stops = compulsory_stops
        self.time_bounds = time_bounds
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix
        self.route_nodes = route_nodes

        self.chosen_nodes_in_seg = {}
        for i in segments:
            self.chosen_nodes_in_seg[i] = []

        self.used_time_in_seg = {}
        for i in segments:
            self.used_time_in_seg[i] = 0

        self.distance_in_seg = {}
        for i in segments:
            self.distance_in_seg[i] = 0

        self.total_cost = 0
        self.total_benefit = 0
        self.served_request_count = 0

    def check_node(self, node):
        segment = node['segment_h'][0]
        check = False

        # Check whether node is compulsory stop
        if node['is_compulsory_stop']:
            check = True
            return check

        if node in self.chosen_nodes_in_seg[segment]:
            check = True
            return check

        # Check whether serving node is feasible
        last_visited = self.chosen_nodes_in_seg[segment][-1]
        curr_time_seg = self.used_time_in_seg[segment]
        time_lv_to_o = self.time_matrix[last_visited['order']][node['order']]
        time_o_to_cs = self.time_matrix[node['order']][self.compulsory_stops[segment]['order']]
        bound_b_seg = self.time_bounds[segment]['b']

        if (curr_time_seg + time_lv_to_o + time_o_to_cs) <= bound_b_seg:
            check = True
            return check
        else:
            return check

    def feasibility_check(self, node_o, node_d):
        bool_o = self.check_node(node_o)
        bool_d = self.check_node(node_d)

        if bool_o and bool_d:
            return True
        else:
            return False

    def greedy_algorithm(self):
        # Add first visited node in each segment, and thus the respective compulsory stop
        for i in self.segments:
            self.chosen_nodes_in_seg[i].append(self.compulsory_stops[i - 1])

        # Add starting time to each segment, and thus the b bound value of the before segment
        for i in self.segments:
            self.used_time_in_seg[i] = self.time_bounds[i - 1]['b']

        # count how many request have been served
        total_distance = 0
        request_count = 0

        for request in self.request_pairs:
            request_o = request['origin']
            request_d = request['destination']

            # Give the request nodes the same form as every other node in route nodes
            # request_o, request_d = ajs.add_values_to_request_node(request_o, request_d)

            if self.feasibility_check(request_o, request_d):
                # increase request count
                request_count += 1

                # Update chosen_nodes_in_seg
                # Check, whether one of the request_nodes falls onto a compulsory stop
                if not request_o['is_compulsory_stop']:
                    segment_o = request_o['segment_h'][0]
                    # check whether the request node is already in the list
                    if request_o not in self.chosen_nodes_in_seg[segment_o]:
                        # Update chosen nodes in segment
                        self.chosen_nodes_in_seg[segment_o].append(request_o)

                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[segment_o][len(self.chosen_nodes_in_seg[segment_o]) - 1]
                        time_lv_to_o = self.time_matrix[last_visited['order']][request_o['order']]
                        self.used_time_in_seg[segment_o] += time_lv_to_o

                        # Update distance in segment
                        distance_lv_to_o = self.distance_matrix[last_visited['order']][request_o['order']]
                        self.distance_in_seg[segment_o] += distance_lv_to_o

                if not request_d['is_compulsory_stop']:
                    segment_d = request_d['segment_h'][0]
                    # check whether the request node is already in the list
                    if request_d not in self.chosen_nodes_in_seg[segment_d]:
                        # Update chosen nodes in segment
                        self.chosen_nodes_in_seg[segment_d].append(request_d)

                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[segment_d][len(self.chosen_nodes_in_seg[segment_d]) - 1]
                        time_lv_to_d = self.time_matrix[last_visited['order']][request_d['order']]
                        self.used_time_in_seg[segment_d] += time_lv_to_d

                        # Update distance in segment
                        distance_lv_to_d = self.distance_matrix[last_visited['order']][request_d['order']]
                        self.distance_in_seg[segment_d] += distance_lv_to_d

        # Connect the last served node in each segment with the next compulsory stop
        for i in self.segments:
            # Update used time in segment i
            last_visited = self.chosen_nodes_in_seg[i][len(self.chosen_nodes_in_seg[i]) - 1]
            time_lv_to_cs = self.time_matrix[last_visited['order']][self.compulsory_stops[i]['order']]

            self.used_time_in_seg[i] += time_lv_to_cs

            # Update chosen nodes in segment i
            self.chosen_nodes_in_seg[i].append(self.compulsory_stops[i])

            # Update distance in segment
            distance_lv_to_cs = self.distance_matrix[last_visited['order']][self.compulsory_stops[i]['order']]
            self.distance_in_seg[i] += distance_lv_to_cs

        # Check whether time in segment is in between a and b
        for i in self.segments:
            if self.used_time_in_seg[i] >= self.time_bounds[i]['a']:
                continue
            else:
                self.used_time_in_seg[i] = self.time_bounds[i]['a']

        # Calculate result
        for i in self.segments:
            total_distance += self.distance_in_seg[i]

        self.total_cost = total_distance
        self.served_request_count = request_count
        self.total_benefit = self.served_request_count * self.benefit_u

        result = self.total_benefit - self.total_cost
        return result

    def main(self):
        """
        Main function to call the other functions
        :return:
        """
        start_time = t.time()
        result = self.greedy_algorithm()
        end_time = t.time()
        print(result)



        # initialize variables for run_instance:

        """
        served_requests, unserved_requests, used_nodes, unused_nodes, total_driven_distance,
        total_travel_time, arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val
        """
        # served_requests
        served_requests = self.served_request_count
        #  unserved_requests
        unserved_requests = len(self.request_pairs) - self.served_request_count

        # used_nodes --> subtract n-1 compulsory stops (= len(self.segments))
        used_nodes = 0
        for i in self.segments:
            used_nodes += len(self.chosen_nodes_in_seg[i])
        used_nodes -= len(self.segments)

        # unused_nodes
        unused_nodes = len(self.route_nodes) - used_nodes

        # total_driven_distance
        total_driven_distance = self.total_cost

        # arrival_time_at_comp_stops
        arrival_time_at_comp_stops = []
        for i in self.segments:
            arrival_time_at_comp_stops.append(self.used_time_in_seg[i])

        solve_time = end_time - start_time

        build_time = None

        opt_gap = None

        obj_val = result

        return (served_requests, unserved_requests, used_nodes, unused_nodes, total_driven_distance,
                arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val)


