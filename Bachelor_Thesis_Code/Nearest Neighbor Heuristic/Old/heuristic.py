import Adjustments as ajs


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

        # new
        self.requests_in_seg = {}
        for i in segments:
            self.requests_in_seg[i] = []

    def check_node(self, node):
        segment = node['segment_h'][0]
        check = False

        # Check whether node is compulsory stop
        if node['is_compulsory_stop']:
            check = True
            return check

        # Check whether serving node_o is feasible
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

    def nearest_neighbor_algorithm(self):
        # map request pairs
        new_request_pairs = ajs.map_request_pairs(self.request_pairs)

        # initialize requests_in_segment
        for i in self.segments:
            for request in new_request_pairs:
                origin = request['origin']
                destination = request['destination']

                # if both are compulsory stops increment served_request_count
                if origin['is_compulsory_stop'] and destination['is_compulsory_stop']:
                    self.served_request_count += 1
                    continue
                # if one is compulsory stop, only add to the segment of the non-compulsory stop
                if not origin['is_compulsory_stop'] and destination['is_compulsory_stop']:
                    if origin['segment_h'][0] == i:
                        self.requests_in_seg[i].append(request)
                    else:
                        continue
                if origin['is_compulsory_stop'] and not destination['is_compulsory_stop']:
                    if destination['segment_h'][0] == i:
                        self.requests_in_seg[i].append(request)
                    else:
                        continue
                # if none is compulsory stop, add to the segment of the origin and destination
                if not origin['is_compulsory_stop'] and not destination['is_compulsory_stop']:
                    if origin['segment_h'][0] == i:
                        self.requests_in_seg[i].append(request)
                    if destination['segment_h'][0] == i:
                        self.requests_in_seg[i].append(request)
                    else:
                        continue

        # start at first compulsory stop
        self.chosen_nodes_in_seg[1].append(self.compulsory_stops[0])

        # search shortest distance to next request node










    def main(self):
        """
        Main function to call the other functions
        :return:
        """
        result = self.greedy_algorithm()
        print("Result:")
        print(result)

        print("Total distance:")
        print(self.total_cost)

        print("Total benefit:")
        print(self.total_benefit)

        print("Served request count:")
        print(self.served_request_count)

        print("Chosen nodes in each segment:")
        for i in self.segments:
            print('segment ' + str(i) + ' :' + str(self.chosen_nodes_in_seg[i]))
