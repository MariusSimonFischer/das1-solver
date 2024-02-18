import time as t
import folium


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

    def visualize(self):

        first_comp_stop = self.route_nodes[0]

        # Create a Folium map centered on the first compulsory stop (you can adjust this)
        map_center = (first_comp_stop['latitude'], first_comp_stop['longitude'])
        my_map = folium.Map(location=map_center, zoom_start=14)

        # Make list of used nodes
        used_nodes = []
        for i in self.segments:
            used_nodes.extend(self.chosen_nodes_in_seg[i])

        # Add markers for used nodes
        for node in used_nodes:
            popup_content = (f"Node Order: {node['order']}, Segment: {node['segment_h']}, "
                             f"Is Compulsory Stop: {node['is_compulsory_stop']}")
            icon_color = 'green' if node['is_compulsory_stop'] else 'blue'
            folium.Marker(
                location=(node['latitude'], node['longitude']),
                popup=popup_content,
                icon=folium.Icon(color=icon_color)
            ).add_to(my_map)

        # Add markers for unused nodes
        for node in self.route_nodes:
            if node not in used_nodes:
                popup_content = (f"Node Order: {node['order']}, Segment: {node['segment_h']}, "
                                 f"Is Compulsory Stop: {node['is_compulsory_stop']}")
                icon_color = 'red' if node['is_compulsory_stop'] else 'gray'
                folium.Marker(
                    location=(node['latitude'], node['longitude']),
                    popup=popup_content,
                    icon=folium.Icon(color=icon_color)
                ).add_to(my_map)

        # Make list of used edges
        used_edges = []
        for i in self.segments:
            for j in range(len(self.chosen_nodes_in_seg[i]) - 1):
                used_edges.append((self.chosen_nodes_in_seg[i][j], self.chosen_nodes_in_seg[i][j + 1]))

        # Add polylines for used edges
        for edge in used_edges:
            coords = [(edge[0]['latitude'], edge[0]['longitude']), (edge[1]['latitude'], edge[1]['longitude'])]
            folium.PolyLine(
                coords,
                color='blue',
                weight=2.5,
                opacity=1
            ).add_to(my_map)

        # Display the map
        my_map.save("solution_map.html")

    def check_node_same_seg(self, node_o, node_d):
        segment = node_o['segment_h'][0]
        check_o = False
        check_d = False

        # Check whether both nodes are already in the list
        if node_o in self.chosen_nodes_in_seg[segment] and node_d in self.chosen_nodes_in_seg[segment]:
            return True

        # Check whether node_o is already in the list
        if node_o in self.chosen_nodes_in_seg[segment]:
            check_o = True

            # check whether serving node_d is feasible
            last_visited = self.chosen_nodes_in_seg[segment][-1]
            curr_time_seg = self.used_time_in_seg[segment]
            time_lv_to_d = self.time_matrix[last_visited['order']][node_d['order']]
            time_d_to_cs = self.time_matrix[node_d['order']][self.compulsory_stops[segment]['order']]
            bound_b_seg = self.time_bounds[segment]['c']

            if (curr_time_seg + time_lv_to_d + time_d_to_cs) <= bound_b_seg:
                check_d = True
                return True
            else:
                return False

        # Check whether node_d is already in the list
        if node_d in self.chosen_nodes_in_seg[segment]:
            check_d = True

            # check whether serving node_o is feasible
            last_visited = self.chosen_nodes_in_seg[segment][-1]
            curr_time_seg = self.used_time_in_seg[segment]
            time_lv_to_o = self.time_matrix[last_visited['order']][node_o['order']]
            time_o_to_cs = self.time_matrix[node_o['order']][self.compulsory_stops[segment]['order']]
            bound_b_seg = self.time_bounds[segment]['c']

            if (curr_time_seg + time_lv_to_o + time_o_to_cs) <= bound_b_seg:
                check_o = True
                return True
            else:
                return False

        # Check whether serving node_o is feasible
        last_visited = self.chosen_nodes_in_seg[segment][-1]
        curr_time_seg = self.used_time_in_seg[segment]
        time_lv_to_o = self.time_matrix[last_visited['order']][node_o['order']]
        time_o_to_cs = self.time_matrix[node_o['order']][self.compulsory_stops[segment]['order']]
        bound_b_seg = self.time_bounds[segment]['c']

        if (curr_time_seg + time_lv_to_o + time_o_to_cs) <= bound_b_seg:
            check_o = True

            # make tmp list to check whether serving node_d is feasible
            tmp_chosen_nodes_list = self.chosen_nodes_in_seg[segment].copy()
            tmp_chosen_nodes_list.append(node_o)

            tmp_used_time = self.used_time_in_seg[segment] + time_lv_to_o

            # check whether serving node_d is feasible
            last_visited = tmp_chosen_nodes_list[-1]
            curr_time_seg = tmp_used_time
            time_lv_to_d = self.time_matrix[last_visited['order']][node_d['order']]
            time_d_to_cs = self.time_matrix[node_d['order']][self.compulsory_stops[segment]['order']]
            bound_b_seg = self.time_bounds[segment]['c']

            if (curr_time_seg + time_lv_to_d + time_d_to_cs) <= bound_b_seg:
                check_d = True

                if check_o and check_d:
                    return True
                else:
                    return False

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
        bound_b_seg = self.time_bounds[segment]['c']

        if (curr_time_seg + time_lv_to_o + time_o_to_cs) <= bound_b_seg:
            check = True
            return check
        else:
            return check

    def feasibility_check(self, node_o, node_d):
        # check whether the segments are the same
        node_o_cs = False
        node_d_cs = False
        # check whether the nodes are compulsory stops
        if node_o['is_compulsory_stop']:
            node_o_cs = True
        if node_d['is_compulsory_stop']:
            node_d_cs = True

        # if both nodes are compulsory stops, the feasibility check is true
        if node_o_cs and node_d_cs:
            return True

        # if one of the nodes is a compulsory stop, check only the other node
        if node_o_cs:
            bool_d = self.check_node(node_d)
            if bool_d:
                return True
            else:
                return False

        if node_d_cs:
            bool_o = self.check_node(node_o)
            if bool_o:
                return True
            else:
                return False

        # if none is a compulsory stop, check both nodes
        # check whether the segments are the same
        if node_o['segment_h'][0] == node_d['segment_h'][0]:
            bool_od = self.check_node_same_seg(node_o, node_d)

            if bool_od:
                return True
            else:
                return False

        bool_o = self.check_node(node_o)
        bool_d = self.check_node(node_d)

        if bool_o and bool_d:
            return True
        else:
            return False

    def nearest_neighbor_heuristic(self):
        # initialize variables
        total_distance = 0
        request_count = 0

        # initialize requests_in_seg
        # Only add none compulsory stops
        for i in self.segments:
            for request in self.request_pairs:
                if not request['origin']['is_compulsory_stop'] and request['origin']['segment_h'][0] == i\
                        and request not in self.requests_in_seg[i]:
                    self.requests_in_seg[i].append(request)
                if not request['destination']['is_compulsory_stop'] and request['destination']['segment_h'][0] == i \
                        and request not in self.requests_in_seg[i]:
                    self.requests_in_seg[i].append(request)

        # if both origin and destination are compulsory stops, increase request count
        for request in self.request_pairs:
            if request['origin']['is_compulsory_stop'] and request['destination']['is_compulsory_stop']:
                request_count += 1

        # add starting time to each segment, and thus the c bound value of the before segment
        for i in self.segments:
            self.used_time_in_seg[i] = self.time_bounds[i - 1]['c']

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

            for i in self.segments:
                if len(self.chosen_nodes_in_seg[i]) > 0:

                    # get back node of current sub path within the segment
                    last_element = self.chosen_nodes_in_seg[i][-1]

                    # check min distance to requests in segment (for last element)
                    if self.requests_in_seg[i] is not None:
                        for request in self.requests_in_seg[i]:

                            # check whether request origin is already in chosen_nodes_in_seg
                            if request['origin'] not in self.chosen_nodes_in_seg[i]:
                                if (not request['origin']['is_compulsory_stop'] and
                                        request['origin']['segment_h'][0] == i):
                                    distance = self.distance_matrix[last_element['order']][request['origin']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        if self.feasibility_check(request['origin'], request['destination']):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            current_winner = 'origin'

                            # check whether request destination is already in chosen_nodes_in_seg
                            if request['destination'] not in self.chosen_nodes_in_seg[i]:
                                if (not request['destination']['is_compulsory_stop'] and
                                        request['destination']['segment_h'][0] == i):
                                    distance = self.distance_matrix[last_element['order']][
                                        request['destination']['order']]
                                    if distance < min_distance:
                                        # check feasibility
                                        if self.feasibility_check(request['origin'], request['destination']):
                                            min_distance = distance
                                            nearest_request = request
                                            current_segment = i
                                            current_winner = 'destination'

            # If no request is feasible, break the loop
            if nearest_request is None:
                break

            # Add nodes of nearest request to segment lists
            # check whether origin or destination node is closer to next element
            if current_winner == 'origin':
                # check whether origin has to be added at all
                if nearest_request['origin'] not in self.chosen_nodes_in_seg[current_segment] \
                        and not nearest_request['origin']['is_compulsory_stop']:
                    # Add origin node to segment list
                    self.chosen_nodes_in_seg[current_segment].append(nearest_request['origin'])
                    # Update used time in segment
                    last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                    time_lv_to_o = self.time_matrix[last_visited['order']][nearest_request['origin']['order']]
                    self.used_time_in_seg[current_segment] += time_lv_to_o

                    # Update distance in segment
                    distance_lv_to_o = self.distance_matrix[last_visited['order']][
                        nearest_request['origin']['order']]
                    self.distance_in_seg[current_segment] += distance_lv_to_o

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
                        distance_lv_to_o = self.distance_matrix[last_visited['order']][
                            nearest_request['origin']['order']]
                        self.distance_in_seg[segment] += distance_lv_to_o

                # check whether destination has to be added at all
                if nearest_request['destination'] not in self.chosen_nodes_in_seg[current_segment] \
                        and not nearest_request['destination']['is_compulsory_stop']:
                    # Add destination node to segment list
                    self.chosen_nodes_in_seg[current_segment].append(nearest_request['destination'])

                    # Update used time in segment
                    last_visited = self.chosen_nodes_in_seg[current_segment][-2]
                    time_lv_to_d = self.time_matrix[last_visited['order']][nearest_request['destination']['order']]
                    self.used_time_in_seg[current_segment] += time_lv_to_d

                    # Update distance in segment
                    distance_lv_to_d = self.distance_matrix[last_visited['order']][
                        nearest_request['destination']['order']]
                    self.distance_in_seg[current_segment] += distance_lv_to_d


            # increase served request count
            if current_winner is not None:
                request_count += 1

                # remove request from requests_in_seg
                # check whether origin and destination fall into same segment
                if not nearest_request['origin']['is_compulsory_stop'] and \
                        not nearest_request['destination']['is_compulsory_stop']:

                    if nearest_request['origin']['segment_h'][0] == nearest_request['destination']['segment_h'][0]:
                        segment = nearest_request['origin']['segment_h'][0]
                        self.requests_in_seg[segment].remove(nearest_request)

                    elif not nearest_request['origin']['is_compulsory_stop']:
                        segment_o = nearest_request['origin']['segment_h'][0]
                        self.requests_in_seg[segment_o].remove(nearest_request)

                    elif not nearest_request['destination']['is_compulsory_stop']:
                        segment_d = nearest_request['destination']['segment_h'][0]
                        self.requests_in_seg[segment_d].remove(nearest_request)

                else:

                    if not nearest_request['origin']['is_compulsory_stop']:
                        segment_o = nearest_request['origin']['segment_h'][0]
                        self.requests_in_seg[segment_o].remove(nearest_request)

                    if not nearest_request['destination']['is_compulsory_stop']:
                        segment_d = nearest_request['destination']['segment_h'][0]
                        self.requests_in_seg[segment_d].remove(nearest_request)

        # Connect the served nodes in each segment with the compulsory stops
        for i in self.segments:

            # Add path between subpath and next compulsory stop
            last_visited = self.chosen_nodes_in_seg[i][-1]
            time_lv_to_cs = self.time_matrix[last_visited['order']][self.compulsory_stops[i]['order']]
            # Update used time in segment i
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
        result = self.nearest_neighbor_heuristic()
        end_time = t.time()

        print(result)



        self.visualize()

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
