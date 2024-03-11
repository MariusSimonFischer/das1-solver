import JSON_loader as jl
import data_mappings as dict_map
import Time_windows as tw
import Gurobi_Solver_DAS as solver
import time_matrix as tm
import time_bound_a_b as tb
import network_x_graph as nxg


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

    # print(dict_map.route_nodes)

    # building a graph by calling the functions from network_x_graph.py
    graph = nxg.main()

    # Initialize the DAS Object
    das = solver.DASOptimizer(benefit_for_request, graph, dict_map.request_pairs, tb.bounds, dict_map.segments,
                              dict_map.delta_origin, dict_map.delta_destination)

    # calling the functions from Gurobi_Solver_DAS.py
    solver.DASOptimizer.main(das)


if __name__ == "__main__":
    main()
