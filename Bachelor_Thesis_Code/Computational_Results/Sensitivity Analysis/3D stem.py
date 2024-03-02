import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np

# Load the DataFrame
df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/data/all1.csv')  # Update the path to your CSV file

# Preparing data for the 3D plot
x = df['benefit']
y = df['served_requests']
z = np.zeros(len(df))  # Base of the stems
dz = df['walking_distance']  # Height of the stems

# Creating the 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plotting the stems
for i in range(len(df)):
    ax.plot([x[i], x[i]], [y[i], y[i]], [z[i], dz[i]], '-b')  # blue stems

# Plotting the markers
ax.scatter(x, y, dz, color='b', s=50)

# Labeling axes
ax.set_xlabel('Benefit')
ax.set_ylabel('Served Requests')
ax.set_zlabel('Walking Distance')

# Setting the title
ax.set_title('3D Stem Plot')

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/3D_plot_requests_served3.pdf')

