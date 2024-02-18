import time as t


class NearestNeighborHeuristic:
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

        self.requests_in_seg = {}
        for i in self.segments:
            self.requests_in_seg[i] = []


    def check_node(self, node, bool):
        segment = node['segment_h'][0]
        check = False

        # Check whether node is compulsory stop
        if node['is_compulsory_stop']:
            check = True
            return check

        if node in self.chosen_nodes_in_seg[segment]:
            check = True
            return check

        # if bool == true check for last element to new node
        # Check whether serving node_o is feasible

        if bool:
            last_visited = self.chosen_nodes_in_seg[segment][-1]
            curr_time_seg = self.used_time_in_seg[segment]
            time_lv_to_o = self.time_matrix[last_visited['order']][node['order']]
            time_o_to_cs1 = self.time_matrix[node['order']][self.compulsory_stops[segment]['order']]
            bound_b_seg = self.time_bounds[segment]['b']

            first_visited = self.chosen_nodes_in_seg[segment][0]
            time_fv_to_cs0 = self.time_matrix[first_visited['order']][self.compulsory_stops[segment - 1]['order']]

            if (curr_time_seg + time_lv_to_o + time_o_to_cs1 + time_fv_to_cs0) <= bound_b_seg:
                check = True
                return check
            else:
                return check

        # if bool == false check for first element to new node
        # Check whether serving node_o is feasible
        if not bool:
            last_visited = self.chosen_nodes_in_seg[segment][-1]
            curr_time_seg = self.used_time_in_seg[segment]
            # time_lv_to_o = self.time_matrix[last_visited['order']][node['order']]
            # time_o_to_cs1 = self.time_matrix[node['order']][self.compulsory_stops[segment]['order']]
            bound_b_seg = self.time_bounds[segment]['b']

            first_visited = self.chosen_nodes_in_seg[segment][0]
            time_fv_to_o = self.time_matrix[first_visited['order']][node['order']]
            time_o_to_cs0 = self.time_matrix[node['order']][self.compulsory_stops[segment - 1]['order']]
            time_lv_to_cs1 = self.time_matrix[last_visited['order']][self.compulsory_stops[segment]['order']]

            if (curr_time_seg + time_fv_to_o + time_o_to_cs0 + time_lv_to_cs1) <= bound_b_seg:
                check = True
                return check
            else:
                return check

    def feasibility_check(self, node_o, node_d, bool_o, bool_d):
        bool_o = self.check_node(node_o, bool_o)
        bool_d = self.check_node(node_d, bool_d)

        if bool_o and bool_d:
            return True
        else:
            # its not feasible anymore, so we remove the request
            return False

    def initialize_first_node_in_segment(self, segment):
        # start from first compulsory stop
        # check distance from first compulsory stop to all requests in first segment

        min_distance = float('inf')
        nearest_request = None
        for request in self.requests_in_seg[segment]:
            distance = self.distance_matrix[self.compulsory_stops[segment-1]['order']][request['origin']['order']]
            if distance < min_distance:
                # check feasibility
                if self.feasibility_check_begin(request['origin'], request['destination']):
                    min_distance = distance
                    nearest_request = request

        # add nodes of nearest request to segment lists
        # get segment for destination node
        if not nearest_request['origin']['is_compulsory_stop']:
            segment1 = nearest_request['origin']['segment_h'][0]
            self.chosen_nodes_in_seg[segment1].append(nearest_request['origin'])

        if not nearest_request['destination']['is_compulsory_stop']:
            segment2 = nearest_request['destination']['segment_h'][0]
            self.chosen_nodes_in_seg[segment2].append(nearest_request['destination'])

        # remove request from requests_in_seg
        if not nearest_request['origin']['is_compulsory_stop']:
            segment_o = nearest_request['origin']['segment_h'][0]
            self.requests_in_seg[segment_o].remove(nearest_request)

        if not nearest_request['destination']['is_compulsory_stop']:
            segment_d = nearest_request['destination']['segment_h'][0]
            self.requests_in_seg[segment_d].remove(nearest_request)



    def nearest_neighbor_heuristic(self):

        total_distance = 0
        request_count = 0

        # initialize requests_in_seg
        # Only add none compulsory stops
        for i in self.segments:
            self.requests_in_seg[i] = [request for request in self.request_pairs
                                       if not request['origin']['is_compulsory_stop']
                                       and request['origin']['segment_h'][0] == i]
            self.requests_in_seg[i] = [request for request in self.request_pairs
                                       if not request['destination']['is_compulsory_stop']
                                       and request['destination']['segment_h'][0] == i]

        # if both origin and destination are compulsory stops, increase request count
        for request in self.request_pairs:
             if request['origin']['is_compulsory_stop'] and request['destination']['is_compulsory_stop']:
                request_count += 1

            # add starting time to each segment, and thus the b bound value of the before segment
        for i in self.segments:
            self.used_time_in_seg[i] = self.time_bounds[i - 1]['b']

        # initialize start position in each segment with respective first compulsory stop
        for i in self.segments:
            self.chosen_nodes_in_seg[i].append(self.compulsory_stops[i - 1])

        # start the algorithm
        amount_of_requests = len(self.request_pairs)
        left_requests = amount_of_requests - request_count

        # amount of times we want to run through the loop
        for _ in range(left_requests):

                # get min distance to next request node in each segment
                min_distance = float('inf')
                nearest_request = None
                current_segment = None
                current_winner = None
                first_element_bool = False
                last_element_bool = False

                for i in self.segments:
                    if len(self.chosen_nodes_in_seg[i]) > 0:

                        # get front and back of current subpath within the segment
                        last_element = self.chosen_nodes_in_seg[i][-1]
                        first_element = self.chosen_nodes_in_seg[i][0]

                        # check min distance to requests in segment (for last element)
                        for request in self.requests_in_seg[i]:

                            # check whether request origin is already in chosen_nodes_in_seg
                            if request['origin'] not in self.chosen_nodes_in_seg[i]:
                                if request['origin']['segment_h'][0] == i and not request['origin']['is_compulsory_stop']:
                                    distance = self.distance_matrix[last_element['order']][request['origin']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        # (True if we add to the back of the current path, otherwise False)
                                        if self.feasibility_check(request['origin'], request['destination'], True, True):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            first_element_bool = False
                                            last_element_bool = True
                                            current_winner = 'origin'

                            # check whether request destination is already in chosen_nodes_in_seg
                            if request['destination'] not in self.chosen_nodes_in_seg[i]:
                                if request['destination']['segment_h'][0] == i and not request['destination']['is_compulsory_stop']:
                                    distance = self.distance_matrix[last_element['order']][request['destination']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        # (True if we add to the back of the current path, otherwise False)
                                        if self.feasibility_check(request['origin'], request['destination'], True, True):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            first_element_bool = False
                                            last_element_bool = True
                                            current_winner = 'destination'

                        # check min distance to requests in segment (for first element)
                        for request in self.requests_in_seg[i]:
                            # check whether request origin is already in chosen_nodes_in_seg
                            if request['origin'] not in self.chosen_nodes_in_seg:
                                if request['origin']['segment_h'][0] == i and not request['origin']['is_compulsory_stop']:
                                    distance = self.distance_matrix[first_element['order']][request['origin']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        # (True if we add to the back of the current path, otherwise False)
                                        if self.feasibility_check(request['origin'], request['destination'], False, True):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            first_element_bool = True
                                            last_element_bool = False
                                            current_winner = 'origin'

                            # check whether request destination is already in chosen_nodes_in_seg
                            if request['destination'] not in self.chosen_nodes_in_seg:
                                if request['destination']['segment_h'][0] == i and not request['destination']['is_compulsory_stop']:
                                    distance = self.distance_matrix[first_element['order']][request['destination']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        # (True if we add to the back of the current path, otherwise False)
                                        if self.feasibility_check(request['origin'], request['destination'], True, False):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            first_element_bool = True
                                            last_element_bool = False
                                            current_winner = 'destination'

                # add nodes of nearest request to segment lists
                # check whether origin or destination node is closer to next element
                if current_winner == 'origin':
                    # check whether origin has to be added at all
                    if nearest_request['origin'] not in self.chosen_nodes_in_seg[current_segment] and nearest_request['origin']['is_compulsory_stop'] == False:

                        # check whether we add to the back or front of the current path
                        if last_element_bool:
                            self.chosen_nodes_in_seg[current_segment].append(nearest_request['origin'])

                            # Update used time in segment
                            last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                            time_lv_to_o = self.time_matrix[last_visited['order']][nearest_request['origin']['order']]
                            self.used_time_in_seg[current_segment] += time_lv_to_o

                            # Update distance in segment
                            distance_lv_to_o = self.distance_matrix[last_visited['order']][nearest_request['origin']['order']]
                            self.distance_in_seg[current_segment] += distance_lv_to_o

                        elif first_element_bool:
                            self.chosen_nodes_in_seg[current_segment].insert(0, nearest_request['origin'])
                            # Update used time in segment
                            first_visited = self.chosen_nodes_in_seg[current_segment][1]
                            time_fv_to_o = self.time_matrix[first_visited['order']][nearest_request['origin']['order']]
                            self.used_time_in_seg[current_segment] += time_fv_to_o

                            # Update distance in segment
                            distance_fv_to_o = self.distance_matrix[first_visited['order']][nearest_request['origin']['order']]
                            self.distance_in_seg[current_segment] += distance_fv_to_o

                    # also add destination node
                    # check whether destination has to be added at all
                    if not nearest_request['destination']['is_compulsory_stop']:
                        segment = nearest_request['destination']['segment_h'][0]
                        if nearest_request['destination'] not in self.chosen_nodes_in_seg[segment]:
                            self.chosen_nodes_in_seg[segment].append(nearest_request['destination'])

                            # Update used time in segment
                            last_visited = self.chosen_nodes_in_seg[segment][-2]
                            time_lv_to_d = self.time_matrix[last_visited['order']][nearest_request['destination']['order']]
                            self.used_time_in_seg[segment] += time_lv_to_d

                            # Update distance in segment
                            distance_lv_to_d = self.distance_matrix[last_visited['order']][nearest_request['destination']['order']]
                            self.distance_in_seg[segment] += distance_lv_to_d


                if current_winner == 'destination':
                    # check whether destination has to be added at all
                    if nearest_request['destination'] not in self.chosen_nodes_in_seg[current_segment] and nearest_request['destination']['is_compulsory_stop'] == False:
                        # check whether we add to the back or front of the current path
                        if last_element_bool:
                            self.chosen_nodes_in_seg[current_segment].append(nearest_request['destination'])

                            # Update used time in segment
                            last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                            time_lv_to_d = self.time_matrix[last_visited['order']][nearest_request['destination']['order']]
                            self.used_time_in_seg[current_segment] += time_lv_to_d

                            # Update distance in segment
                            distance_lv_to_d = self.distance_matrix[last_visited['order']][
                                nearest_request['destination']['order']]
                            self.distance_in_seg[current_segment] += distance_lv_to_d

                        elif first_element_bool:
                            self.chosen_nodes_in_seg[current_segment].insert(0, nearest_request['destination'])

                            # Update used time in segment
                            first_visited = self.chosen_nodes_in_seg[current_segment][1]
                            time_fv_to_d = self.time_matrix[first_visited['order']][nearest_request['destination']['order']]
                            self.used_time_in_seg[current_segment] += time_fv_to_d

                            # Update distance in segment
                            distance_fv_to_d = self.distance_matrix[first_visited['order']][
                                nearest_request['destination']['order']]
                            self.distance_in_seg[current_segment] += distance_fv_to_d

                    # also add origin node
                    # check whether origin has to be added at all
                    if not nearest_request['origin']['is_compulsory_stop']:
                        segment = nearest_request['origin']['segment_h'][0]
                        if nearest_request['origin'] not in self.chosen_nodes_in_seg[segment]:
                            self.chosen_nodes_in_seg[segment].append(nearest_request['origin'])

                            # Update used time in segment
                            last_visited = self.chosen_nodes_in_seg[segment][-2]
                            time_lv_to_o = self.time_matrix[last_visited['order']][nearest_request['origin']['order']]
                            self.used_time_in_seg[segment] += time_lv_to_o

                            # Update distance in segment
                            distance_lv_to_o = self.distance_matrix[last_visited['order']][nearest_request['origin']['order']]
                            self.distance_in_seg[segment] += distance_lv_to_o










        total_distance = 0
        request_count = 0

        # initialize requests_in_seg
        # Only add none compulsory stops
        for i in self.segments:
            self.requests_in_seg[i] = [request for request in self.request_pairs
                                       if not request['origin']['is_compulsory_stop']
                                       and request['origin']['segment_h'][0] == i]
            self.requests_in_seg[i] = [request for request in self.request_pairs
                                       if not request['destination']['is_compulsory_stop']
                                       and request['destination']['segment_h'][0] == i]

        # if both origin and destination are compulsory stops, increase request count
        for i in self.segments:
            for request in self.request_pairs:
                if request['origin']['is_compulsory_stop'] and request['destination']['is_compulsory_stop']:
                    request_count += 1

        # add starting time to each segment, and thus the b bound value of the before segment
        for i in self.segments:
            self.used_time_in_seg[i] = self.time_bounds[i - 1]['b']

        # counter which segment has to be initialized
        x = 1
        self.initialize_first_node_in_segment(x) # was wenn es nicht funktioniert hat?
        # increase served request count
        request_count += 1

        # start the algorithm
        amount_of_requests = len(self.request_pairs)
        left_requests = amount_of_requests - request_count

        # amount of times we want to run through the loop
        for _ in range(left_requests):

            # get min distance to next request node in each segment
            min_distance = float('inf')
            nearest_request = None
            current_segment = None
            current_winner = None
            first_element_bool = False
            last_element_bool = False
            for i in self.segments:
                check = False
                # check whether algorithm can still work
                if not self.requests_in_seg[x]:
                    for j in self.segments:
                        j += 1
                        if not self.chosen_nodes_in_seg[j + 1]:
                            check = True

                if check:
                    x += 1
                    self.initialize_first_node_in_segment(x)
                    # increase served request count
                    request_count += 1

                if len(self.chosen_nodes_in_seg[i]) > 0:
                    # get front and back of subpath
                    last_element = self.chosen_nodes_in_seg[i][-1]
                    first_element = self.chosen_nodes_in_seg[i][0]

                    # check min distance to requests in segment (for last element)
                    for request in self.requests_in_seg[i]:
                        if request not in self.chosen_nodes_in_seg[i]:
                            if request['origin']['segment_h'][0] == i and not request['origin']['is_compulsory_stop']:
                                distance = self.distance_matrix[last_element['order']][request['origin']['order']]
                                if distance < min_distance:
                                    # check feasibility
                                    if self.feasibility_check(request['origin'], request['destination'], True, True):
                                        min_distance = distance
                                        nearest_request = request
                                        current_segment = i
                                        first_element_bool = False
                                        last_element_bool = True
                                        current_winner = 'origin'
                            if request['destination']['segment_h'][0] == i and not request['destination']['is_compulsory_stop']:
                                distance = self.distance_matrix[last_element['order']][request['destination']['order']]
                                if distance < min_distance:
                                    # check feasibility
                                    if self.feasibility_check(request['origin'], request['destination'], True, True):
                                        min_distance = distance
                                        nearest_request = request
                                        current_segment = i
                                        first_element_bool = False
                                        last_element_bool = True
                                        current_winner = 'destination'

                    # check min distance to requests in segment (for first element)
                    for request in self.requests_in_seg[i]:
                        if request not in self.chosen_nodes_in_seg[i]:
                            if request['origin']['segment_h'][0] == i and not request['origin']['is_compulsory_stop']:
                                distance = self.distance_matrix[first_element['order']][request['origin']['order']]
                                if distance < min_distance:
                                    # check feasibility
                                    if self.feasibility_check(request['origin'], request['destination'], False, True):
                                        min_distance = distance
                                        nearest_request = request
                                        current_segment = i
                                        first_element_bool = True
                                        last_element_bool = False
                                        current_winner = 'origin'
                            if request['destination']['segment_h'][0] == i and not request['destination']['is_compulsory_stop']:
                                distance = self.distance_matrix[first_element['order']][request['destination']['order']]
                                if distance < min_distance:
                                    # check feasibility
                                    if self.feasibility_check(request['origin'], request['destination'], True, False):
                                        min_distance = distance
                                        nearest_request = request
                                        current_segment = i
                                        first_element_bool = True
                                        last_element_bool= False
                                        current_winner = 'destination'

            # add nodes of nearest request to segment lists
            # check whether origin or destination node is closer to next element
            if current_winner == 'origin':
                # check whether origin has to be added at all
                if nearest_request['origin'] not in self.chosen_nodes_in_seg[current_segment] \
                        and nearest_request['origin']['is_compulsory_stop'] == False:
                    if last_element_bool:
                        self.chosen_nodes_in_seg[current_segment].append(nearest_request['origin'])
                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                        time_lv_to_o = self.time_matrix[last_visited['order']][nearest_request['origin']['order']]
                        self.used_time_in_seg[current_segment] += time_lv_to_o

                        # Update distance in segment
                        distance_lv_to_o = self.distance_matrix[last_visited['order']][
                            nearest_request['origin']['order']]
                        self.distance_in_seg[current_segment] += distance_lv_to_o

                    elif first_element_bool:
                        self.chosen_nodes_in_seg[current_segment].insert(0, nearest_request['origin'])
                        # Update used time in segment
                        first_visited = self.chosen_nodes_in_seg[current_segment][1]
                        time_fv_to_o = self.time_matrix[first_visited['order']][nearest_request['origin']['order']]
                        self.used_time_in_seg[current_segment] += time_fv_to_o

                        # Update distance in segment
                        distance_fv_to_o = self.distance_matrix[first_visited['order']][
                            nearest_request['origin']['order']]
                        self.distance_in_seg[current_segment] += distance_fv_to_o

                # also add destination node
                # check whether destination has to be added at all
                if not nearest_request['destination']['is_compulsory_stop']:
                    segment = nearest_request['destination']['segment_h'][0]
                    if nearest_request['destination'] not in self.chosen_nodes_in_seg[segment]:
                        self.chosen_nodes_in_seg[segment].append(nearest_request['destination'])

                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[segment][-2]
                        time_lv_to_d = self.time_matrix[last_visited['order']][nearest_request['destination']['order']]
                        self.used_time_in_seg[segment] += time_lv_to_d

                        # Update distance in segment
                        distance_lv_to_d = self.distance_matrix[last_visited['order']][
                            nearest_request['destination']['order']]
                        self.distance_in_seg[segment] += distance_lv_to_d

            if current_winner == 'destination':
                segment = nearest_request['destination']['segment_h'][0]
                # check whether destination has to be added at all
                if nearest_request['destination'] not in self.chosen_nodes_in_seg[segment] \
                        and nearest_request['destination']['is_compulsory_stop'] == False:
                    if last_element_bool:
                        self.chosen_nodes_in_seg[current_segment].append(nearest_request['destination'])

                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                        time_lv_to_d = self.time_matrix[last_visited['order']][nearest_request['destination']['order']]
                        self.used_time_in_seg[current_segment] += time_lv_to_d

                        # Update distance in segment
                        distance_lv_to_d = self.distance_matrix[last_visited['order']][
                            nearest_request['destination']['order']]
                        self.distance_in_seg[current_segment] += distance_lv_to_d

                    elif first_element_bool:
                        self.chosen_nodes_in_seg[current_segment].insert(0, nearest_request['destination'])

                        # Update used time in segment
                        first_visited = self.chosen_nodes_in_seg[current_segment][1]
                        time_fv_to_d = self.time_matrix[first_visited['order']][nearest_request['destination']['order']]
                        self.used_time_in_seg[current_segment] += time_fv_to_d

                        # Update distance in segment
                        distance_fv_to_d = self.distance_matrix[first_visited['order']][
                            nearest_request['destination']['order']]
                        self.distance_in_seg[current_segment] += distance_fv_to_d

                # also add origin node
                # check whether origin has to be added at all
                if not nearest_request['origin']['is_compulsory_stop']:
                    segment = nearest_request['origin']['segment_h'][0]
                    if nearest_request['origin'] not in self.chosen_nodes_in_seg[segment]:
                        self.chosen_nodes_in_seg[segment].append(nearest_request['origin'])

                        # Update used time in segment
                        last_visited = self.chosen_nodes_in_seg[segment][-2]
                        time_lv_to_o = self.time_matrix[last_visited['order']][nearest_request['origin']['order']]
                        self.used_time_in_seg[segment] += time_lv_to_o

                        # Update distance in segment
                        distance_lv_to_o = self.distance_matrix[last_visited['order']][nearest_request['origin']['order']]
                        self.distance_in_seg[segment] += distance_lv_to_o

            # increase served request count
            if current_winner is not None:
                request_count += 1
                # remove request from requests_in_seg
                if not nearest_request['origin']['is_compulsory_stop']:
                    segment_o = nearest_request['origin']['segment_h'][0]
                    self.requests_in_seg[segment_o].remove(nearest_request)

                if not nearest_request['destination']['is_compulsory_stop']:
                    segment_d = nearest_request['destination']['segment_h'][0]
                    self.requests_in_seg[segment_d].remove(nearest_request)

        # Connect the served nodes in each segment with the compulsory stops

        for i in self.segments:
            # Update used time in segment i
            # check whether list saving the served nodes in segment is empty
            if len(self.chosen_nodes_in_seg[i]) == 0:
                continue
            last_visited = self.chosen_nodes_in_seg[i][-1]
            time_lv_to_cs = self.time_matrix[last_visited['order']][self.compulsory_stops[i]['order']]

            self.used_time_in_seg[i] += time_lv_to_cs

            first_visited = self.chosen_nodes_in_seg[i][0]
            time_fv_to_cs = self.time_matrix[first_visited['order']][self.compulsory_stops[i - 1]['order']]

            self.used_time_in_seg[i] += time_fv_to_cs

            # Update chosen nodes in segment i
            self.chosen_nodes_in_seg[i].append(self.compulsory_stops[i])
            self.chosen_nodes_in_seg[i].insert(0, self.compulsory_stops[i - 1])

            # Update distance in segment
            distance_lv_to_cs = self.distance_matrix[last_visited['order']][self.compulsory_stops[i]['order']]
            self.distance_in_seg[i] += distance_lv_to_cs

            distance_fv_to_cs = self.distance_matrix[first_visited['order']][self.compulsory_stops[i - 1]['order']]
            self.distance_in_seg[i] += distance_fv_to_cs

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
        result = self.nearest_neighbor_heuristic()
        end_time = t.time()
        print(result)
