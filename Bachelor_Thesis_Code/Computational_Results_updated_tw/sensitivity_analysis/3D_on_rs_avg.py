import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np

# Load your DataFrame as 'df'
df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/b_and_wd_on_sr_higher_numbers.csv')

# Calculate averages for each combination of 'benefit' and 'walking_distance'
grouped = df.groupby(['benefit', 'walking_distance'])['served_requests'].mean().reset_index()

# Preparing data for the 3D stem plot
x = grouped['benefit']
y = grouped['walking_distance']
z = grouped['served_requests']

# Creating the 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Create stem plot
for xi, yi, zi in zip(x, y, z):
    ax.plot([xi, xi], [yi, yi], [0, zi], marker="_", color='b')  # This plots the stem.
    ax.plot([xi], [yi], [zi], marker="o", color='b')  # This plots the point at the top.

# Labeling axes
ax.set_xlabel('Benefit', fontsize=12)
ax.set_ylabel('Walking Distance', fontsize=12)
ax.set_zlabel('Average Served Requests', fontsize=12)

plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/b_and_wd_onsr_3D_test_higher_numbers.pdf')
