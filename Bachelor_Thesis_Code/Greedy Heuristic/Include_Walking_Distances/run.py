import JSON_loader as jl
import DataMappings as dict_map
import heuristic as heuristic_solver


def main():
    # Load the JSON file into a dictionary
    data = jl.main()

    # Walking distance
    walking_distance = 700

    # calling the functions from DataMappings.py
    dict_map.main(data, walking_distance)

    # benefit is static with value 1 for now
    benefit_for_request = 1000

    # Initialize the GreedyHeuristic Object
    obj = (heuristic_solver.GreedyHeuristic(benefit_for_request,
                                            dict_map.segments,
                                            dict_map.request_pairs,
                                            dict_map.compulsory_stops,
                                            dict_map.bounds,
                                            dict_map.distance_matrix,
                                            dict_map.time_matrix,
                                            dict_map.route_nodes))

    # calling the functions from GreedyHeuristic
    heuristic_solver.GreedyHeuristic.main(obj)




if __name__ == "__main__":
    main()
