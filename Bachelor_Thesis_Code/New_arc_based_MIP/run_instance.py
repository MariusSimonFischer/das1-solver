import csv
import os
import JSONLoader as jl
import Gurobi_Solver_DAS as solver
import DataMappings as dict_map
import network_x_g as nxg


def save_data_in_csv(data, fn):
    """
    Save the data in a csv file.
    :param data: data to be saved
    :param fn: file name
    :return: None
    """

    columns = ['route', 'route_starting_time', 'percentage_of_compulsory_stops', 'benefit', 'walking_distance',
               'num_segments', 'compulsory_stops',
               'requests', 'number_optional_stops',
               'used_nodes', 'unused_nodes', 'unserved_requests', 'served_requests',
               'opt_stops_visited', 'opt_stops_not_visited',
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

    # walking distance is static
    walking_distance = walking_distance

    # calling the functions from DataMappings.py
    dict_map.main(data, walking_distance)

    # benefit is static
    benefit_for_request = benefit_u

    total_requests_count = dict_map.total_requests_count

    # Building a graph by calling the functions from network_x_graph.py
    graph = nxg.main()

    # Initialize the DAS Object
    das = solver.DASOptimizer(benefit_for_request, graph, dict_map.request_pairs, dict_map.bounds, dict_map.segments,
                              dict_map.delta_origin, dict_map.delta_destination)

    # calling the functions from Gurobi_Solver_DAS.py
    (num_segments, num_requests, served_requests, unserved_requests, used_nodes, unused_nodes,
     total_driven_distance, num_opt_stops, num_opt_stops_visited, num_opt_stops_not_visited,
     total_travel_time, arrival_time_at_comp_stops, solve_time, build_time, opt_gap, obj_val) \
        = solver.DASOptimizer.main(das)

    compulsory_stops = dict_map.compulsory_stops
    requests = dict_map.request_pairs
    served_requestsx = served_requests
    used_nodesx = len(used_nodes)
    unused_nodesx = len(unused_nodes)
    optional_stops_visited = used_nodesx - len(compulsory_stops)
    travel_distance = total_driven_distance
    arrival_time_at_comp_stopsx = arrival_time_at_comp_stops
    unserved_requestsx = total_requests_count - len(served_requests)
    solve_timex = solve_time
    build_timex = build_time
    opt_gapx = opt_gap
    obj_valx = obj_val

    return (num_segments, total_requests_count, num_opt_stops, num_opt_stops_visited, num_opt_stops_not_visited,
            compulsory_stops, requests, served_requestsx, used_nodesx, unused_nodesx,
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

    # Get all the scenario files
    scenario_files = os.listdir(path)

    # Run the instances
    for scenario in scenario_files:
        route = scenario.split('_')[0]
        route_time = scenario.split('_')[1] + ':' + scenario.split('_')[2] + ':' + scenario.split('_')[3]
        percentage_of_copt_stops = scenario.split('_')[4]
        # optional_dist = scenario.split('_')[5]
        # comp_dist = scenario.split('_')[6]
        # seed = scenario.split('_')[7].split('.')[0]

        # Run the instances for different benefit values and walking distances
        for wd in walking_distances:
            for benefit in benefit_u:
                try:
                    (num_segments, num_requests, num_opt_stops, num_opt_stops_visited, num_opt_stops_not_visited,
                     comp_stops, requests, served_requests, used_nodes, unused_nodes,
                     optional_stops_visited, travel_distance,
                     arrival_at_cs, unserved_requests, solve_time, build_time, optimality_gap, obj_val) \
                        = run_instance(path + f'/{scenario}', benefit, wd)

                    total_used_travel_time = arrival_at_cs[-1] - arrival_at_cs[0]

                    data = [route, route_time, percentage_of_copt_stops, benefit, wd,
                            num_segments,
                            len(comp_stops), num_requests, num_opt_stops,
                            used_nodes, unused_nodes, unserved_requests, len(served_requests),
                            optional_stops_visited, num_opt_stops_not_visited,
                            total_used_travel_time, travel_distance, build_time, solve_time, optimality_gap, obj_val]
                except:
                    data = [route, route_time, percentage_of_copt_stops, benefit, wd,
                            None, None, None, None, None, None, None, None, None, None, None, None, None,
                            None, None, None]

                # Save the data in a csv file
                csv_f = os.path.dirname(os.path.realpath(__file__)) + '/results/run_test.csv'
                save_data_in_csv(data, csv_f)


if __name__ == '__main__':
    current_folder = os.path.dirname(os.path.realpath(__file__))
    pathx = os.path.join(current_folder, os.pardir, 'jsons', 'jsons_updated_new_tw', 'jsons_new_tw')

    walking_distancesx = [700]
    benefit_ux = [1000]

    run_several_instances(pathx, benefit_ux, walking_distancesx)
