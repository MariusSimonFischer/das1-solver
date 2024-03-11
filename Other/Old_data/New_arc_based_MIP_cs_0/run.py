import JSONLoader as jl
import DataMappings as dict_map
import network_x_g as nxg
import Gurobi_Solver_DAS as solver

def main():
    # Load the JSON file into a dictionary
    data = jl.main()

    # calling the functions from DataMappings.py
    dict_map.main(data)

    # benefit is static
    benefit_for_request = 1000

    # building a graph by calling the functions from network_x_graph.py
    graph = nxg.main()

    # print('Number of nodes: ', len(dict_map.route_nodes))
    # print('Number of cs: ', len(dict_map.compulsory_stops))
    # print('Number of requests: ', len(dict_map.request_pairs))

    # Initialize the DAS Object
    das = solver.DASOptimizer(benefit_for_request, graph, dict_map.request_pairs, dict_map.bounds, dict_map.segments,
                          dict_map.delta_origin, dict_map.delta_destination)

    # calling the functions from Gurobi_Solver_DAS.py
    solver.DASOptimizer.main(das)


if __name__ == "__main__":
    main()