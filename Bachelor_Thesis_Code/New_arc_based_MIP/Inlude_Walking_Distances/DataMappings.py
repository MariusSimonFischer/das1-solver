from datetime import datetime

""""
This script is used to create a new Data foundation with the following properties:
    - Only the nodes that are in the request pairs are kept
    - The distance matrix is updated accordingly
    - The order of the nodes is redefined, so that the first node has order 0, the second node has order 1, etc.

More specifically, the following steps are performed:
    1. Find the shortest distance from each building to the next node
    2. Create "request pairs" by coupling the origin and destination node
    3. Create new route nodes by leaving nodes with "is_compulsory_stop": true and nodes that are in the "request pairs"
    4. Update distance matrix by deleting rows and columns of nodes that are not in the new route nodes
    5. Redefine order of nodes in new_route_nodes by iterating over new_route_nodes and changing the order of the nodes
    making the order fit the distance matrix again
"""



data = None
walking_distance = None

min_distance_and_node = []

request_pairs = []
route_nodes = []

distance_matrix = []
segments = []
delta_origin = {}
delta_destination = {}

time_matrix = []
compulsory_stops = []
bounds = []
time_windows = []

total_requests_count = 0


def find_min_distance_and_node():
    """
    Find the shortest distance from each building to the next node and save it in a dictionary
    :return: shortest_distances: dictionary with the shortest distances from each building to the next node
    """
    global min_distance_and_node
    min_distance_and_node = []

    curr_request = -1
    # Iterating over the entries in 'buildings_distance_matrix'
    for entry in data['buildings_distance_matrix']:
        curr_request += 1
        # Find min distance to next node for each building
        min_distance = 0
        min_distance_node = None
        for i in range(len(entry)):
            if i == 0:
                min_distance = entry[i]
                min_distance_node = data['route_nodes'][i]
            else:
                if entry[i] < min_distance:
                    min_distance = entry[i]
                    min_distance_node = data['route_nodes'][i]
        # Append the min distance and the node to the list
        tmp_location = data['sampled_building_pairs'][curr_request]['location']
        tmp_trip_id = data['sampled_building_pairs'][curr_request]['trip_id']

        min_distance_and_node.append({'min_distance': min_distance, 'node': min_distance_node,
                                      'location': tmp_location, 'trip_id': tmp_trip_id})

    return min_distance_and_node


def build_request_pairs():
    """
    Build request pairs by coupling the origin and destination node
    :return:
    """
    global request_pairs
    request_pairs = []
    global total_requests_count
    total_requests_count = 0

    # Coupling origin and destination node as request:
    for entry1 in min_distance_and_node:
        for entry2 in min_distance_and_node:
            if (entry1['trip_id'] == entry2['trip_id'] and
                    entry1['location'] == 'origin' and entry2['location'] == 'destination'):

                # Check whether walking distance is fullfilled:
                # Only add a request if both nodes are within walking distance
                total_requests_count += 1

                if entry1['min_distance'] <= walking_distance and entry2['min_distance'] <= walking_distance:

                    request_pairs.append(
                        {'origin': entry1['node'], 'destination': entry2['node'], 'trip_id': entry1['trip_id']})

    return request_pairs


def make_list_of_dicts_distinct(list_of_dicts, key):
    seen_values = set()
    result = []

    for d in list_of_dicts:
        value = d.get(key)
        if value not in seen_values:
            seen_values.add(value)
            result.append(d)

    return result


def create_new_route_nodes():
    """
    Create new route nodes by leaving compulsory stops and nodes that are in the "request pairs"
    Now only compulsory stops and nodes that are origin or destination of a request are left
    :return:
    """
    global route_nodes
    route_nodes = []

    for node in data['route_nodes']:
        # check whether node is in request_pairs
        for pair in request_pairs:
            if (node['latitude'] == pair['origin']['latitude'] and
                    node['longitude'] == pair['origin']['longitude'] and node not in route_nodes):
                route_nodes.append(node)
            elif (node['latitude'] == pair['destination']['latitude'] and
                  node['longitude'] == pair['destination']['longitude'] and node not in route_nodes):
                route_nodes.append(node)

    for node in data['route_nodes']:
        # check whether node is compulsory stop
        for entry in data['time_windows']:
            if entry['node_id'] == node['node_id'] and node not in route_nodes:
                route_nodes.append(node)
                break

    # make sure compulsory stops are only added once
    new_route_nodes = make_list_of_dicts_distinct(route_nodes, key="order")

    route_nodes = new_route_nodes

    # sort route_nodes by order
    route_nodes = sorted(route_nodes, key=lambda k: k['order'])

    return route_nodes


def add_is_compulsory_stop():
    """
    Function to add is_compulsory_stop to route_nodes
    :return:
    """
    global route_nodes

    for entry in route_nodes:
        for node in data['time_windows']:
            if entry['node_id'] == node['node_id']:
                entry['is_compulsory_stop'] = True
                break
        else:
            entry['is_compulsory_stop'] = False
    return route_nodes


def update_distance_matrix():
    """
    Function to update the distance matrix by deleting rows and columns of nodes that are not in the new route nodes
    :return:
    """
    global distance_matrix
    distance_matrix = []

    new_order_list = []
    # find all orders (indices) of nodes in new_route_nodes
    for entry in route_nodes:
        new_order_list.append(entry['order'])

    # make it distinct (in case there were several requests at the same node)
    new_order_list = list(set(new_order_list))

    # iterate over current_route_nodes and find the distances to all other nodes
    for node in route_nodes:
        node_order = node['order']
        distances = data['distance_matrix'][node_order]

        new_distances = []
        # only keep the distances that are at the indices of the nodes in new_route_nodes
        # (i.e. delete all distances that are not in new_route_nodes)
        for i in range(len(distances)):
            if i in new_order_list:
                new_distances.append(distances[i])

        distance_matrix.append(new_distances)

    return distance_matrix


def update_time_matrix():
    """
    Function to update the time matrix by deleting rows and columns of nodes that are not in the new route nodes
    :return:
    """
    global time_matrix
    time_matrix = []

    new_order_list = []
    # find all orders (indices) of nodes in new_route_nodes
    for entry in route_nodes:
        new_order_list.append(entry['order'])

    # make it distinct (in case there were several requests at the same node)
    new_order_list = list(set(new_order_list))

    # iterate over current_route_nodes and find the needed time to all other nodes
    for node in route_nodes:
        node_order = node['order']
        times = data['travel_time_matrix'][node_order]

        new_times = []
        # only keep the distances that are at the indices of the nodes in new_route_nodes
        # (i.e. delete all distances that are not in new_route_nodes)
        for i in range(len(times)):
            if i in new_order_list:
                new_times.append(times[i])

        time_matrix.append(new_times)

    return time_matrix


def redefine_order():
    """
    Function to redefine the order of nodes in new_route_nodes by iterating over new_route_nodes and changing the order
    of the nodes from 0 to n-1
    :return:
    """
    global route_nodes
    # first sort route_nodes by order
    route_nodes = sorted(route_nodes, key=lambda k: k['order'])

    # iterate over route_nodes and update order
    for i in range(len(route_nodes)):
        route_nodes[i]['order'] = i
    return route_nodes


def add_segment_h():
    """
    Function to add segment_h to route_nodes
    :return:
    """
    global route_nodes
    current_segment = 0

    for entry in route_nodes:
        if entry['is_compulsory_stop']:
            current_segment += 1
            entry['segment_h'] = [current_segment - 1, current_segment]
        else:
            entry['segment_h'] = [current_segment]
    return route_nodes


def add_is_origin_and_is_destination():
    """
    Function to add is_origin and is_destination to route_nodes
    :return:
    """
    global route_nodes
    n = 0
    for entry in route_nodes:
        if entry['is_compulsory_stop']:
            n += 1
            if n == 1:
                entry['is_origin'] = True
            else:
                entry['is_origin'] = False
        else:
            entry['is_origin'] = False

    # count number of compulsory stops
    tmp_list = []
    for entry in route_nodes:
        if entry['is_compulsory_stop']:
            tmp_list.append(entry)

    for entry in route_nodes:
        if entry['is_compulsory_stop'] and entry['order'] == tmp_list[len(tmp_list) - 1]['order']:
            entry['is_destination'] = True
        else:
            entry['is_destination'] = False

    return route_nodes


def init_segments_list():
    """
    Function to initialize the segments list
    :return:
    """
    global segments
    segments = []
    n = 0
    for entry in route_nodes:
        if entry['is_compulsory_stop']:
            n += 1
            segments.append(n)
    # remove segment after last compulsory stop

    # check whether there are compulsory stops
    if len(segments) > 0:
        segments.remove(n)
    return segments


def initialize_delta():
    """
    Function to initialize delta
    :return:
    """
    global delta_origin
    global delta_destination
    delta_origin = {}
    delta_destination = {}
    # iterate over request_pairs
    for i in range(len(request_pairs)):
        # iterate over route_nodes
        delta_origin[i] = []
        delta_destination[i] = []
        for node in route_nodes:
            if node['latitude'] == request_pairs[i]['origin']['latitude'] \
                    and node['longitude'] == request_pairs[i]['origin']['longitude']:
                delta_origin[i].append(1)
            else:
                delta_origin[i].append(0)

            if node['latitude'] == request_pairs[i]['destination']['latitude'] \
                    and node['longitude'] == request_pairs[i]['destination']['longitude']:
                delta_destination[i].append(1)
            else:
                delta_destination[i].append(0)

    return delta_origin, delta_destination


def reduce_to_compulsory_stops():
    """
    Function to reduce route_nodes to compulsory stops
    """
    global compulsory_stops
    compulsory_stops = []
    for node in route_nodes:
        if node['is_compulsory_stop']:
            compulsory_stops.append(node)
    return compulsory_stops


def time_string_to_seconds(time_str):
    """
    Function to convert a time string into seconds since midnight
    :param time_str:
    :return:
    """
    # Parse the time string into a datetime object
    time_object = datetime.strptime(time_str, '%H:%M:%S')

    # Calculate the total seconds since midnight
    seconds_since_midnight = time_object.hour * 3600 + time_object.minute * 60 + time_object.second

    return seconds_since_midnight


def define_bounds():
    """
    Function to define the a and b bounds
    """
    global time_windows
    time_windows = []
    global bounds
    bounds = []

    time_windows = data['time_windows']

    for entry in time_windows:
        bounds.append({'a': time_string_to_seconds(entry['time_window']['earliest_departure_time']),
                       'b': time_string_to_seconds(entry['time_window']['latest_departure_time'])})


def main(json_data, walking_dist):
    """
    Main function to call all other functions
    :param json_data: data from JSON_loader
    :return:
    """
    global data
    data = json_data

    global walking_distance
    walking_distance = walking_dist

    # find min distance and node for each building
    find_min_distance_and_node()
    # build request pairs:
    build_request_pairs()
    # Create new route nodes and save them in route_nodes
    create_new_route_nodes()
    # Add is_compulsory_stop to route_nodes
    add_is_compulsory_stop()
    # Update distance matrix and save it in distance_matrix
    update_distance_matrix()
    # Update time matrix and save it in time_matrix
    update_time_matrix()
    # Redefine order of nodes in route_nodes and save them in route_nodes
    redefine_order()
    # Add segment_h to route_nodes
    add_segment_h()
    # Init segments list
    init_segments_list()
    # Add is_origin and is_destination to route_nodes
    add_is_origin_and_is_destination()
    # Initialize delta
    initialize_delta()
    # Reduce route_nodes to compulsory stops
    reduce_to_compulsory_stops()
    # Define bounds
    define_bounds()

    # Testing---------------------------


if __name__ == "__main__":
    main()
