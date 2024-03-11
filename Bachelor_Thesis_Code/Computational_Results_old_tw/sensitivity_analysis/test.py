import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

df = pd.read_csv('/Bachelor_Thesis_Code/Computational_Results_old_tw/Sensitivity Analysis/data/all1.csv')

# Calculate the averages
averages_df = df.groupby(['x', 'y'])['z'].mean().reset_index()

# 3D Stem plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Data for the stems
xs = averages_df['x']
ys = averages_df['y']
zs = np.zeros_like(xs)  # Starting points of the stems (zeroes)

# Data for the stem ends (average z values)
z_top = averages_df['z']

# Plot each stem
for (x, y, z, zt) in zip(xs, ys, zs, z_top):
    line = np.linspace(z, zt, 10)  # 10 points between z and zt for a smooth line
    ax.plot([x, x], [y, y], zs=[z, zt], marker='_', markersize=10)

# Labeling axes
ax.set_xlabel('Benefit')
ax.set_ylabel('Walking Distance')
ax.set_zlabel('Served Requests')

plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/test.pdf')
