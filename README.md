# DAS Scheduling
This repository implements three solving mechanisms for a DAS1 scheduling problem. Thereby, two heuristics (an adapted
Nearest Neighbour Heuristic, and Greedy Heuristic) and one MIP Solver (Gurobi Solver) is used.
Federico Malucelli, Maddalena Nonato & Stefano Pallottino published the paper building the foundation to this analysis [link to paper](https://link.springer.com/chapter/10.1057/9780230372924_8).

This code is part of a Bachelor Thesis written at the Professorship of Business Analytics & Intelligent Systems at TU München.

# Structure
In the Bachelor_Thesis_Code directory, you find the used data, solving algorithms and analtical results used for the thesis.
The sub-directories include different parts of the project. The directory jsons contains the provided data from the Chair.
Greed_Heuristic includes the Greedy Algorithm, Nearest_Neighbour_Heuristic is the directory for the adapted Nearest Neighbour Algorithm and New_arc_based_MIP contains the Gurobi Solver implementation. The two Computational_Results directories simply include analytical graphs and data outputs used for analysis within the Bachelor Thesis.

# Running the Algorithm

1. Running the Gurobi Solver: To run all instances the run_instances







To run the algorithm you should run the following in your IDE terminal: *python generators\Segmentation.py [width_type] [instance] [speed] [number_of_samples] [dimension_of_samples] [standard_deviation] [epsilon] [time_window_width].* The following input arguments are valid:

| Argument | Input|
| ---------|----------|
| width_type | fixed,adjustable |
| instance | This represents the instance number, each instance in the data directory has an instance number, this can be found in \data\routes (e.g. Design_0-14-10-0.8-0.2_hybrid has the instance number 14) |
| speed | Set of whole numbers |
| number_of_samples | Set of whole numbers |
| dimension_of_samples | Set of whole numbers |
| standard_deviation | 0 - 100 |
| epsilon | 0 - 1  |
| time_window_width | Set of whole numbers |

Running the algorithm with the fixed widht and the instance 22 with a 10 samples and 10 dimensions for each sample and with a speed argument of 25 and standard deviation value of 2, epsilon value of 0.05 and the time_window_width of 5 can be done via *python generators\Segmentation.py fixed 22 25 10 10 2 0.05 5.*
