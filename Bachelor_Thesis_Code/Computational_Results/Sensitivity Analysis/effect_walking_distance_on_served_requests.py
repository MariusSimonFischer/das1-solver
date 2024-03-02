import pandas as pd
import matplotlib.pyplot as plt

# Replace 'your_file_path.csv' with the actual path to your CSV file
file_path = '/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/data/all_walking_distance2.csv'

# Load the CSV file into a DataFrame
data = pd.read_csv(file_path)

# Grouping the data by 'walking_distance' and calculating the mean for 'served_requests' and 'unserved_requests'
mean_values = data.groupby('walking_distance')[['served_requests', 'unserved_requests']].mean().reset_index()

# Plotting the line graph
plt.figure(figsize=(12, 8))
plt.plot(mean_values['walking_distance'], mean_values['served_requests'], label='Average Served Requests', marker='o', color = 'blue')
plt.plot(mean_values['walking_distance'], mean_values['unserved_requests'], label='Average Unserved Requests', marker='x', color = 'red')

# Adding title and labels
# plt.title('Impact of Walking Distance on Served and Unserved Requests')
plt.xlabel('Walking Distance', fontsize=12)
plt.ylabel('Average Number of Requests', fontsize=12)

# Adding legend
plt.legend()

# Adding grid for better readability
plt.grid(True)

# Ensuring layout is tight so everything fits without overlapping
plt.tight_layout()

plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/effect_wd_on_sr1.pdf')

