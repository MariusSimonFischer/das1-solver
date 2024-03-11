import JSONLoader as jl
import DataMappings as dict_map
import network_x_g as nxg
import Gurobi_Solver_DAS as solver

def main():
    # Load the JSON file into a dictionary
    data = jl.main()

    # Walking distance
    walking_distance = 700

    # calling the functions from DataMappings.py
    dict_map.main(data, walking_distance)

    # benefit is static
    benefit_for_request = 1000

    # building a graph by calling the functions from network_x_graph.py
    graph = nxg.main()

    # print('Number of nodes: ', len(dict_map.route_nodes))
    # print('Number of cs: ', len(dict_map.compulsory_stops))
    # print('Number of requests: ', len(dict_map.request_pairs))

    # Testing:
    # print distance between node with order 0 and node with order 6
    # print("Distance 0 to 6: ", dict_map.distance_matrix[0][6])

    # print distance between node 0 to 5 to 4 to 6
    # print("Distance 0 to 5 to 4: ", dict_map.distance_matrix[0][5] + dict_map.distance_matrix[5][4] + dict_map.distance_matrix[4][6])


    # Initialize the DAS Object
    das = solver.DASOptimizer(benefit_for_request, graph, dict_map.request_pairs, dict_map.bounds, dict_map.segments,
                          dict_map.delta_origin, dict_map.delta_destination)

    # calling the functions from Gurobi_Solver_DAS.py
    solver.DASOptimizer.main(das)


if __name__ == "__main__":
    main()