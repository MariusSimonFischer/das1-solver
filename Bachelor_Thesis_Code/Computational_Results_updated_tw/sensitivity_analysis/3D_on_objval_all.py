import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

# Assuming 'route_55_test6_df' is your DataFrame
df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/b_and_wd_on_sr.csv')




# Preparing data for the 3D scatter plot
x_ov = df['benefit']
y_ov = df['walking_distance']
z_ov = df['obj_val']

# Creating the 3D scatter plot
fig = plt.figure(figsize=(12, 8))
ax2 = fig.add_subplot(111, projection='3d')

scatter2 = ax2.scatter(x_ov, y_ov, z_ov, c=z_ov, cmap='coolwarm', marker='o')
ax2.set_xlabel('Benefit (units)', fontsize=12)
ax2.set_ylabel('Walking Distance (meters)', fontsize=12)
ax2.set_zlabel('Objective Value', fontsize=12)
cbar = fig.colorbar(scatter2, ax=ax2, shrink=0.5, aspect=5)
cbar.set_label('Objective Value (units)', fontsize=12)

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/b_and_wd_on_objv_3D_all_new.pdf')

