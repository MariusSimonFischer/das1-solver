import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

# Assuming you have loaded your DataFrame as 'df'
# Replace 'df' with the name of your DataFrame variable
df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/b_and_wd_on_sr.csv')

# Preparing data for the 3D plot
x = df['benefit']
y = df['walking_distance']
z = df['served_requests']

# Creating the 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot in 3D
scatter = ax.scatter(x, y, z, c=z, cmap='coolwarm', marker='o')

# Labeling axes
ax.set_xlabel('Benefit', fontsize=12)
ax.set_ylabel('Walking Distance', fontsize=12)
ax.set_zlabel('Served Requests', fontsize=12)

# Adding a color bar
cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5)
cbar.set_label('Served Requests')

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/b_and_wd_onsr_3D.pdf')


"""
x_ov = route_55_test4_df['benefit']
y_ov = route_55_test4_df['walking_distance']
z_ov = route_55_test4_df['objective_value']

fig = plt.figure(figsize=(12, 8))
ax2 = fig.add_subplot(111, projection='3d')

scatter2 = ax2.scatter(x_ov, y_ov, z_ov, c=z_ov, cmap='coolwarm', marker='o')
ax2.set_xlabel('Benefit')
ax2.set_ylabel('Walking Distance')
ax2.set_zlabel('Objective Value')
ax2.set_title('Benefit, Walking Distance vs. Objective Value')
fig.colorbar(scatter2, ax=ax2, shrink=0.5, aspect=5, label='Objective Value')

plt.show()
"""
