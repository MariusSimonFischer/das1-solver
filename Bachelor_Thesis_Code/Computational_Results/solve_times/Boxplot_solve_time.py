
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


# Load the data
gurobi_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_GurobiSolver.csv')
nearest_neighbour_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_NearestNeighbourHeuristic.csv')
greedy_df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/data/solving_times1_GreedyHeuristic.csv')

# Standardize column names and add a 'method' column to each DataFrame
gurobi_df['method'] = 'Gurobi Solver'
nearest_neighbour_df.rename(columns={'solve_time': 'solve_time'}, inplace=True)
nearest_neighbour_df['method'] = 'Nearest Neighbour Heuristic'
greedy_df.rename(columns={'solve_time': 'solve_time'}, inplace=True)
greedy_df['method'] = 'Greedy Heuristic'


# Combine the dataframes
combined_df = pd.concat([gurobi_df[['solve_time', 'method']],
                         nearest_neighbour_df[['solve_time', 'method']],
                         greedy_df[['solve_time', 'method']]])

# Plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='method', y='solve_time', data=combined_df, color='k', palette=['0.75', '0.5', '0.25'])
plt.ylabel('Solve Time (seconds)')
plt.xlabel('Method')
plt.yscale('log')  # Using a logarithmic scale due to wide range of solve times
#plt.xticks(rotation=45)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/solve_times/results/box_plot_solve_times.pdf')



# Calculating descriptive statistics for solve times by method
descriptive_stats = combined_df.groupby('method')['solve_time'].describe()

# Adding interquartile range (IQR) and range
descriptive_stats['IQR'] = descriptive_stats['75%'] - descriptive_stats['25%']
descriptive_stats['Range'] = descriptive_stats['max'] - descriptive_stats['min']

# Reordering columns to include IQR and Range
descriptive_stats = descriptive_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'IQR', 'max', 'Range']]

# Resetting index for better display
descriptive_stats.reset_index(inplace=True)

print(descriptive_stats)
