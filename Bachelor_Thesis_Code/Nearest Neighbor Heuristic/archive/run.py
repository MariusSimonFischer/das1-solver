import JSON_loader as jl
import data_mappings as dict_map
import Time_windows as tw
import time_matrix as tm
import time_bound_a_b as tb
import heuristic as heuristic_solver


def main():
    # Load the JSON file into a dictionary
    data = jl.main()

    # calling the functions from DataMappings.py
    dict_map.main(data)

    # calling the functions from Time_windows.py
    tw.main()

    # benefit is static with value 1 for now
    benefit_for_request = 5000

    # calling the functions from time_bound_a_b.py
    tb.main()
    # print(tb.bounds)

    # checking the order, which is not yet correct!!!
    """
    for entry in dict_map.route_nodes:
        if entry['is_compulsory_stop']:
            print(entry['segment_h'])
            print(entry['order'])
    print(dict_map.route_nodes[27])
    """

    # calling the functions from time_matrix.py
    tm.main()
    # print(tm.time_matrix)

    # Initialize the GreedyHeuristic Object
    obj = (heuristic_solver.GreedyHeuristic(benefit_for_request,
                                            dict_map.segments,
                                            dict_map.request_pairs,
                                            tw.compulsory_stops,
                                            tb.bounds,
                                            dict_map.distance_matrix,
                                            tm.time_matrix,
                                            dict_map.route_nodes))

    # calling the functions from GreedyHeuristic
    heuristic_solver.GreedyHeuristic.main(obj)




if __name__ == "__main__":
    main()
