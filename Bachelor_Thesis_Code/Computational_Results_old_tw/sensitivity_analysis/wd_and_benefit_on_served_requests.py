import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("/Bachelor_Thesis_Code/Computational_Results_old_tw/Sensitivity Analysis/data/all1.csv")

# Group data by 'benefit' and 'walking_distance' and calculate the mean 'served_requests'
grouped_df = df.groupby(['benefit', 'walking_distance'])['served_requests'].mean().reset_index()

# Determine the maximum served requests to establish a "relatively high" threshold
max_served_requests = grouped_df['served_requests'].max()
relatively_high_threshold = 0.9 * max_served_requests

# Filter for combinations achieving relatively high served requests
relatively_high_df = grouped_df[grouped_df['served_requests'] >= relatively_high_threshold]

# Find the combination with the lowest benefit within the relatively high served requests
optimal_case = relatively_high_df.loc[relatively_high_df['benefit'].idxmin()]

# Visualization
plt.figure(figsize=(10, 6))
scatter = plt.scatter(grouped_df['benefit'], grouped_df['served_requests'], c=grouped_df['walking_distance'], cmap='viridis', alpha=0.6, marker='x')
plt.scatter(optimal_case['benefit'], optimal_case['served_requests'], color='red', s=100, edgecolors='black', label='Optimal Point (Benefit=400, WD=400)', marker='x')
plt.colorbar(scatter, label='Walking Distance' )
plt.xlabel('Benefit', fontsize=12)
plt.ylabel('Served Requests', fontsize=12)
# plt.title('Benefit vs. Served Requests Colored by Walking Distance')
plt.legend()
plt.grid(True)

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/benefit_and_wd_on_served_requests.pdf')
