import data_mappings as dict_map


def add_values_to_request_node(origin_node, destination_node):
    # add missing values to each
    # [{'latitude': 48.1014135, 'longitude': 11.6463103, 'is_compulsory_stop': True,
    # 'order': 0, 'segment_h': [0, 1], 'is_origin': True, 'is_destination': False}
    for entry in dict_map.route_nodes:
        if entry['latitude'] == origin_node['latitude'] and entry['longitude'] == origin_node['longitude']:
            origin_node['is_compulsory_stop'] = entry['is_compulsory_stop']
            origin_node['order'] = entry['order']
            origin_node['segment_h'] = entry['segment_h']
            origin_node['is_origin'] = entry['is_origin']
            origin_node['is_destination'] = entry['is_destination']
        else:
            continue
    for entry in dict_map.route_nodes:
        if (entry['latitude'] == destination_node['latitude'] and
                entry['longitude'] == destination_node['longitude']):
            destination_node['is_compulsory_stop'] = entry['is_compulsory_stop']
            destination_node['order'] = entry['order']
            destination_node['segment_h'] = entry['segment_h']
            destination_node['is_origin'] = entry['is_origin']
            destination_node['is_destination'] = entry['is_destination']
        else:
            continue
    return origin_node, destination_node


def map_request_pairs(request_pairs):
    mapped_request_pairs = []
    for request in request_pairs:
        origin = request['origin']
        destination = request['destination']
        origin, destination = add_values_to_request_node(origin, destination)
        mapped_request_pairs.append({'origin': origin, 'destination': destination})
    return mapped_request_pairs
