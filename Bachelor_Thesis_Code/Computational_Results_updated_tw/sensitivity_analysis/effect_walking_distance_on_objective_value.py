import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = '/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/effect_wd_on_sr_gurobi_25.csv'
data = pd.read_csv(file_path)

# Calculate the mean objective values for each walking distance
mean_objective_values = data.groupby('walking_distance')['obj_val'].mean().reset_index()

# Plot the line graph for mean objective value vs. walking distance
plt.figure(figsize=(12, 8))
plt.plot(mean_objective_values['walking_distance'], mean_objective_values['obj_val'], color='blue', marker='o')

# plt.title('Mean Objective Value vs. Walking Distance', fontsize=16)
plt.xlabel('Walking Distance', fontsize=12)
plt.ylabel('Objective Value', fontsize=12)

plt.grid(True)
plt.tight_layout()

plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/effect_wd_on_objval_25.pdf')

