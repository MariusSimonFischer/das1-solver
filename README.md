# DAS Scheduling
This repository implements three solving mechanisms for a DAS1 scheduling problem. Thereby, two heuristics (an adapted
Nearest Neighbour Heuristic, and Greedy Heuristic) and one MIP Solver (Gurobi Solver) is used.
For further information on research: Federico Malucelli, Maddalena Nonato & Stefano Pallottino published a paper building the foundation to this analysis [link to paper](https://link.springer.com/chapter/10.1057/9780230372924_8).

This code is part of a Bachelor Thesis written at the Professorship of Business Analytics & Intelligent Systems at TU München.

# Structure
In the Bachelor_Thesis_Code directory, you find the used data, solving algorithms and analytical results used for the thesis.
The sub-directories include different parts of the project. The directory jsons contains the provided data from the Chair.
Greedy_Heuristic includes the Greedy Algorithm, Nearest_Neighbour_Heuristic is the directory for the adapted Nearest Neighbour Algorithm and New_arc_based_MIP contains the Gurobi Solver implementation. The two Computational_Results directories simply include analytical graphs and data outputs used for analysis within the Bachelor Thesis.

Within the Solving Algorithm directories, the following files are included:
- run_instance.py: The file to run the algorithms for all instances
- run.py: The file to run the algorithm for a single instance
- JSONLoader.py: The file to load the data from the json file
- DataMappings.py: The file to adjust data for the underlying problem
- heuristic.py/ Gurobi_Solver_DAS.py: The files to implement the solving algorithms
- solution_map.html: HTML code to visualize the solution of a single instance on a map
- networkx_graph.py: The file to build a networkx graph for the Gurobi_Solver_DAS.py

Furthermore, the Gurobi Algorithm can be run without realizing optional stops by using the file Gurobi_Solver_DAS_no_optional_stops.py and adjusting Gurobi_Solver_DAS.py accordingly (uncommenting section: # Case without optional stops).

# Running the Algorithms
All three algorithms can be run using the same workflow:

To run all instances the run_instance.py file within each directory can be used. The file can be run via the terminal with the command *python .../run_instance.py* or via the file directly. The file can be modified to run only specific instances or to change input and output directories and names. The file will run the Gurobi Solver for all instances and save the results (a Table with comprehensive statistics) in the specified directory (currently results). The source data and directory name as well as parameters "Walking Distance" and "Benefit" can be changed in the run_instance.py file. Furthermore, the other python files include the logic behind. If only one specific instance should be run, the run.py can be used and the json can be specified in JSONLoader.py. The solution_map.html shows a map visualization of the single instance run with run.py (open for example in browser).

1. Running the Gurobi Solver: *python New_arc_based_MIP/run_instance.py* 
2. Running the Greedy Algorithm: *python Greedy_Heuristic/run_instance.py* 
3. Running the Nearest Neighbour Algorithm: *python Nearest_Neighbour_Heuristic/run_instance.py* 
