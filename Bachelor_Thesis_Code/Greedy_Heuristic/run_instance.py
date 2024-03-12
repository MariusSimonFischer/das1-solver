import csv
import os
import JSON_loader as jl
import heuristic as solver
import DataMappings as dict_map


def save_data_in_csv(data, fn):
    """
    Save the data in a csv file.
    :param data: data to be saved
    :param fn: file name
    :return: None
    """

    columns = ['route', 'route_time', 'percentage_comp_stops', 'benefit', 'walking_distance', 'compulsory_stops',
               'requests', 'used-nodes', 'unused_nodes', 'unserved_requests', 'served_requests',
               'optional_stops_visited',
               'total_used-travel_time', 'travel_distance',
               'build_time', 'solve_time', 'optimality_gap', 'obj_val']

    if not os.path.isfile(fn):
        with open(fn, 'w', newline='') as file:
            # Ceate csv file and write the column names
            writer = csv.writer(file)
            writer.writerow(columns)

    with open(fn, 'a', newline='') as file:
        # Append the data to the csv file
        writer = csv.writer(file)
        writer.writerow(data)


def run_instance(json, benefit_u, walking_distance):
    """
    Function to run an instance of the DAS problem
    :return: None
    """
    data = jl.load_json(json)

    # calling the functions from DataMappings.py
    dict_map.main(data, walking_distance)

    # benefit is static
    benefit_for_request = benefit_u

    # Initialize the DAS Object
    greedy_heuristic = solver.GreedyHeuristic(benefit_for_request, dict_map.segments, dict_map.request_pairs,
                                              dict_map.compulsory_stops, dict_map.bounds, dict_map.distance_matrix,
                                              dict_map.time_matrix, dict_map.route_nodes)

    # calling the functions from heuristic.py
    (served_requests, unserved_requests, used_nodes, unused_nodes, total_driven_distance,
        arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val) \
        = solver.GreedyHeuristic.main(greedy_heuristic)

    compulsory_stops = dict_map.compulsory_stops
    requests = dict_map.request_pairs
    served_requestsx = served_requests
    used_nodesx = used_nodes
    unused_nodesx = unused_nodes
    optional_stops_visited = used_nodesx - len(compulsory_stops)
    travel_distance = total_driven_distance
    arrival_time_at_comp_stopsx = arrival_time_at_comp_stops
    unserved_requestsx = unserved_requests
    solve_timex = solve_time
    build_timex = build_time
    opt_gapx = opt_gap
    obj_valx = obj_val

    return (compulsory_stops, requests, served_requestsx, used_nodesx, unused_nodesx,
            optional_stops_visited, travel_distance, arrival_time_at_comp_stopsx,
            unserved_requestsx, solve_timex, build_timex, opt_gapx, obj_valx)


def run_several_instances(path, benefit_u, walking_distances):
    """
    Function to run several instances of the DAS problem
    :param path:
    :param benefit_u:
    :param walking_distances:
    :return:
    """
    scenario_files = os.listdir(path)

    for scenario in scenario_files:
        route = scenario.split('_')[0]
        route_time = scenario.split('_')[1] + ':' + scenario.split('_')[2] + ':' + scenario.split('_')[3]
        percentage_of_copt_stops = scenario.split('_')[4]
        # optional_dist = scenario.split('_')[5]
        # comp_dist = scenario.split('_')[6]
        # seed = scenario.split('_')[7].split('.')[0]

        for wd in walking_distances:
            for benefit in benefit_u:
                try:
                    (comp_stops, requests, served_requests, used_nodes, unused_nodes,
                     optional_stops_visited, travel_distance,
                     arrival_at_cs, unserved_requests, solve_time, build_time, optimality_gap, obj_val) \
                        = run_instance(path + f'/{scenario}', benefit, wd)

                    total_used_travel_time = arrival_at_cs[-1] - arrival_at_cs[0]

                    data = [route, route_time, percentage_of_copt_stops, benefit, wd, len(comp_stops), len(requests),
                            used_nodes, unused_nodes, unserved_requests, served_requests,
                            optional_stops_visited,
                            total_used_travel_time, travel_distance, build_time, solve_time, optimality_gap, obj_val]
                except:
                    data = [route, route_time, percentage_of_copt_stops, benefit, wd,
                            None, None, None, None, None, None, None, None, None, None, None, None, None]

                csv_f = os.path.dirname(os.path.realpath(__file__)) + '/results/run_test.csv'
                save_data_in_csv(data, csv_f)


if __name__ == '__main__':
    current_folder = os.path.dirname(os.path.realpath(__file__))
    pathx = os.path.join(current_folder, os.pardir, 'jsons', 'jsons_updated_new_tw', 'jsons_new_tw')

    benefit_ux = [1000]
    walking_distancesx = [700]

    run_several_instances(pathx, benefit_ux, walking_distancesx)

