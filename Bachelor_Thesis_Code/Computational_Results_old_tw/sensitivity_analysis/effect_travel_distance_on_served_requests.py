import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = '/Bachelor_Thesis_Code/Computational_Results_old_tw/Sensitivity Analysis/data/all_ben_wd.csv'
data = pd.read_csv(file_path)

# Creating bins for travel distance with a reasonable interval
data['distance_bin'] = pd.cut(data['travel_distance'], bins=10)

# Calculating the average number of served requests for each bin
avg_served_requests_per_bin = data.groupby('distance_bin')['served_requests'].mean().reset_index()

# Extracting the mid-point of each bin to use as the x-axis values for a clearer representation
avg_served_requests_per_bin['bin_mid'] = avg_served_requests_per_bin['distance_bin'].apply(lambda x: x.mid)

# Setting the aesthetic style of the plots
sns.set_style("whitegrid")

# Plotting the line graph
plt.figure(figsize=(12, 8))
plt.plot(avg_served_requests_per_bin['bin_mid'], avg_served_requests_per_bin['served_requests'], marker='o', linestyle='-', color = 'blue')
# plt.title('Average Served Requests by Travel Distance Interval')
plt.xlabel('Travel Distance', fontsize=12)
plt.ylabel('Average Served Requests',   fontsize=12)
plt.tight_layout()
plt.grid(True)



# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/effect_travel_distance_on_served_requests.pdf')
