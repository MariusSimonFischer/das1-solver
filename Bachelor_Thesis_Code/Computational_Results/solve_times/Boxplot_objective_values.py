import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
# Load the data
gurobi_solver_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_GurobiSolver.csv')
nearest_neighbour_heuristic_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_NearestNeighbourHeuristic.csv')
greedy_heuristic_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_GreedyHeuristic.csv')


# Add a 'method' column to each DataFrame
gurobi_solver_df['method'] = 'Gurobi Solver'
nearest_neighbour_heuristic_df['method'] = 'Nearest Neighbour Heuristic'
greedy_heuristic_df['method'] = 'Greedy Heuristic'

# Standardize the objective value column name across all dataframes
# For Gurobi Solver, use 'obj_val' directly
nearest_neighbour_heuristic_df.rename(columns={'obj_val': 'obj_val'}, inplace=True)
greedy_heuristic_df.rename(columns={'obj_val': 'obj_val'}, inplace=True)

# Combine the dataframes
combined_df = pd.concat([
    gurobi_solver_df[['obj_val', 'method']],
    nearest_neighbour_heuristic_df[['obj_val', 'method']],
    greedy_heuristic_df[['obj_val', 'method']]
])

# Plot with the same layout as the provided box plot but adjusted for 'objective_value'
plt.figure(figsize=(10, 6))
sns.boxplot(x='method', y='obj_val', data=combined_df, color='k', palette=['0.75', '0.5', '0.25'])
plt.ylabel('Objective Value')
plt.xlabel('Method')
plt.xticks(rotation=0)
plt.tight_layout()

# Show the plot
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/results/box_plot_objective_values.pdf')




# To perform the analysis on how much better the Gurobi Solver is compared to the heuristic methods,
# we will calculate the percentage improvement of the Gurobi Solver's objective values over the heuristic methods.

# Extract the median objective values for each method
median_values = descriptive_stats_obj_val_part2.set_index('method')['50%']

# Calculate the percentage improvement of Gurobi Solver over each heuristic method
improvement_over_greedy = (median_values['Gurobi Solver'] - median_values['Greedy Heuristic']) / abs(median_values['Greedy Heuristic']) * 100
improvement_over_nearest_neighbour = (median_values['Gurobi Solver'] - median_values['Nearest Neighbour Heuristic']) / abs(median_values['Nearest Neighbour Heuristic']) * 100

improvement_over_greedy, improvement_over_nearest_neighbour
