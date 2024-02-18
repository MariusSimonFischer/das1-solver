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

data = 0
shortest_distances = []
request_pairs = []
route_nodes = []
distance_matrix = []
segments = []
delta_origin = {}
delta_destination = {}


def find_shortest_distance():
    """
    Find the shortest distance from each building to the next node and save it in a dictionary
    :return: shortest_distances: dictionary with the shortest distances from each building to the next node
    """

    # Erstellen eines leeren Dictionaries, um die kürzesten Entfernungen von building zu node zu speichern
    global shortest_distances
    shortest_distances = []

    # Iterieren über jeden Eintrag in 'walking_distance_between_buildings_and_nodes'
    for entry in data['walking_distance_between_buildings_and_nodes']:
        building = entry['building']
        node = entry['node']
        distance = entry['distance']

        # wenn shortest_distances/ entries liste noch leer ist, wird der erste Eintrag hinzugefügt
        if not shortest_distances:
            shortest_distances.append({'building': building, 'node': node, 'distance': distance})
            continue

        # Überprüfen, ob die Entfernung bereits für das aktuelle Gebäude gespeichert ist
        for tmp_entry in shortest_distances:
            tmp_building = tmp_entry['building']
            if tmp_building == building:
                # Überprüfen, ob die Entfernung kürzer ist als die aktuell gespeicherte Entfernung
                if distance < tmp_entry['distance']:
                    # Aktualisieren der Entfernung
                    tmp_entry['distance'] = distance
                    tmp_entry['node'] = node

        # Hinzufügen des Eintrags, falls er noch nicht existiert
        if not any(tmp_entry['building'] == building for tmp_entry in shortest_distances):
            shortest_distances.append({'building': building, 'node': node, 'distance': distance})

    # 'shortest_distances' enthält nun die kürzesten Entfernungen zum nächsten Node und den Node selbst für jedes
    # Gebäude
    return shortest_distances


def create_request_pairs():
    """
    Create "request pairs" by coupling the origin and destination node
    request pairs are those nodes that are the closest to the origin and destination of a request respectively
    :return:
    """
    global request_pairs
    request_pairs = []

    # Coupling origin und destination node als request:
    for pair in data['sampled_building_pairs']:
        origin = pair['origin']
        origin_latitude = origin['latitude']
        origin_longitude = origin['longitude']
        destination = pair['destination']
        destination_latitude = destination['latitude']
        destination_longitude = destination['longitude']

        # Find the origin node in shortest_distances
        for entry_origin in shortest_distances:
            building_origin = entry_origin['building']
            building_origin_latitude = building_origin['latitude']
            building_origin_longitude = building_origin['longitude']

            # Check whether the building is the origin building
            if building_origin_latitude == origin_latitude and building_origin_longitude == origin_longitude:
                # Find the destination node in shortest_distances
                for entry_dest in shortest_distances:
                    building_dest = entry_dest['building']
                    building_dest_latitude = building_dest['latitude']
                    building_dest_longitude = building_dest['longitude']

                    if (building_dest_latitude == destination_latitude
                            and building_dest_longitude == destination_longitude):
                        request_pairs.append(
                            {'origin': entry_origin['node'], 'destination': entry_dest['node']})

    return request_pairs


def create_new_route_nodes():
    """
    Create new route nodes by leaving nodes with "is_compulsory_stop": true and nodes that are in the "request pairs"
    Now only compulsory stops and nodes that are origin or destination of a request are left
    :return:
    """
    global route_nodes
    route_nodes = []
    for node in data['route_nodes']:
        # check whether node is compulsory stop
        if node['is_compulsory_stop']:
            route_nodes.append(node)
        else:
            # check whether node is in request_pairs
            for pair in request_pairs:
                if (node['latitude'] == pair['origin']['latitude'] and
                        node['longitude'] == pair['origin']['longitude']):
                    route_nodes.append(node)
                elif (node['latitude'] == pair['destination']['latitude'] and
                      node['longitude'] == pair['destination']['longitude']):
                    route_nodes.append(node)

    # before returning, make new_route_nodes distinct
    new_route_nodes_distinct = [dict(t) for t in {tuple(d.items()) for d in route_nodes}]
    # Order them by order
    new_route_nodes_distinct = sorted(new_route_nodes_distinct, key=lambda k: k['order'])

    route_nodes = new_route_nodes_distinct

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
    for order in route_nodes:
        new_order_list.append(order['order'])
    # make it distinct (in case there were several requests at the same node)
    new_order_list = list(set(new_order_list))

    # iterate over current_route_nodes and find the distances to all other nodes
    for node in route_nodes:
        node_order = node['order']
        distances = data['distance_matrix_between_nodes'][node_order]

        new_distances = []
        # only keep the distances that are at the indices of the nodes in new_route_nodes
        # (i.e. delete all distances that are not in new_route_nodes)
        for i in range(len(distances)):
            if i in new_order_list:
                new_distances.append(distances[i])

        distance_matrix.append(new_distances)

    return distance_matrix


def redefine_order():
    """
    Function to redefine the order of nodes in new_route_nodes by iterating over new_route_nodes and changing the order
    of the nodes from 0 to n-1
    :return:
    """
    global route_nodes
    for i in range(len(route_nodes)):
        route_nodes[i]['order'] = i
    return route_nodes


# Add segment_h to each node in route_nodes
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
    segments.remove(n)
    return segments

# Test how results change if not only the actual node with its request is taken into account, but also nodes that are
# close to the request (i.e. within 200m)
"""
# calculate distance in meters between node and request
def calculate_distance(lat1, lon1, lat2, lon2):
    
    # Radius of the Earth in meters
    radius_earth = 6371.0 * 1000.0  # Converted from kilometers to meters

    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Calculate differences in latitudes and longitudes
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula to calculate distance
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = radius_earth * c
    return distance


# calculate delta_origin and delta_destination
def init_request_dictionaries():
    
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
            distance_origin = calculate_distance(node['latitude'],
                                                 node['longitude'],
                                                 request_pairs[i]['origin']['latitude'],
                                                 request_pairs[i]['origin']['longitude'])

            distance_destination = calculate_distance(node['latitude'],
                                                      node['longitude'],
                                                      request_pairs[i]['destination']['latitude'],
                                                      request_pairs[i]['destination']['longitude'])

            if distance_origin <= 200:
                delta_origin[i].append(1)
            else:
                delta_origin[i].append(0)

            if distance_destination <= 200:
                delta_destination[i].append(1)
            else:
                delta_destination[i].append(0)

    return delta_origin, delta_destination
"""


def initialize_delta():
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


def main(json_data):
    """
    Main function to call all other functions
    :param json_data: data from JSON_loader
    :return:
    """
    global data
    data = json_data

    # Find the shortest distances and save them in shortest_distances
    find_shortest_distance()
    # print(shortest_distances)

    # Create request pairs and save them in request_pairs
    create_request_pairs()
    # print(request_pairs)

    # Create new route nodes and save them in route_nodes
    create_new_route_nodes()


    # Update distance matrix and save it in distance_matrix
    update_distance_matrix()
    # print(distance_matrix)

    # Redefine order of nodes in route_nodes and save them in route_nodes
    redefine_order()
    # print(route_nodes)

    # Add segment_h to route_nodes
    add_segment_h()
    # print(route_nodes)
    # print(len(route_nodes))

    # Init segments list
    init_segments_list()
    # print(segments)

    # Add is_origin and is_destination to route_nodes
    add_is_origin_and_is_destination()

    # Initialize delta
    initialize_delta()
    # print(delta_origin)
    # print(delta_destination)


# Call main function
if __name__ == "__main__":
    main()

    """
    # Find the shortest distances and save them in shortest_distances
    shortest_distances = find_shortest_distance(data)
    print(shortest_distances['entries'])

    # Create request pairs and save them in request_pairs
    request_pairs = create_request_pairs(shortest_distances)
    print(request_pairs['entries'])

    # Create new route nodes and save them in route_nodes
    route_nodes = create_new_route_nodes(data['route_nodes'], request_pairs)

    # Update distance matrix and save it in distance_matrix
    distance_matrix = update_distance_matrix(data['distance_matrix_between_nodes'], route_nodes)
    print(distance_matrix)

    # Redefine order of nodes in route_nodes and save them in route_nodes
    route_nodes = redefine_order(route_nodes)
    print(route_nodes)

    # Testing the functions---------------------------------------------------------------------------------------------
    
    shortest_distances_dict = find_shortest_distance(data)

    request_pairs_dict = create_request_pairs(shortest_distances_dict)

    # Testausgabe, um zu überprüfen, ob requests verloren gehen
    print(request_pairs_dict['entries'])

    #check whether request_pairs_dict is distinct
    for i in range(len(request_pairs_dict['entries'])):
        for j in range(i+1, len(request_pairs_dict['entries'])):
            if request_pairs_dict['entries'][i] == request_pairs_dict['entries'][j]:
                print("duplicate")

    amount_of_requests_now = len(request_pairs_dict['entries'])
    amount_of_requests_originally = len(data['sampled_building_pairs'])

    print(f"Amount of requested node pairs now: {amount_of_requests_now}")
    print(f"Amount of requests originally: {amount_of_requests_originally}")

    # Count route nodes
    route_nodes = data['route_nodes']
    amount_of_route_nodes = len(route_nodes)
    print(f"Amount of route nodes: {amount_of_route_nodes}")


    #Testing create_new_route_nodes
    new_route_nodes = create_new_route_nodes(route_nodes, request_pairs_dict)
    print(f"Amount of new route nodes: {len(new_route_nodes)}")
    print(new_route_nodes)

    #Testing update_distance_matrix
    distance_matrix = data['distance_matrix_between_nodes']
    new_distance_matrix = update_distance_matrix(distance_matrix, new_route_nodes)
    print(new_distance_matrix)

    #Testing redefine_order
    new_route_nodes_new_order = redefine_order(new_route_nodes)
    print(new_route_nodes)
    """
