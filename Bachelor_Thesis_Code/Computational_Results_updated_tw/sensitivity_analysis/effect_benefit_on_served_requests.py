import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = '/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/effect_b_on_sr_gurobi_50.2.csv'
df = pd.read_csv(file_path)


# Grouping the data by 'walking_distance' and calculating the mean for 'served_requests' and 'unserved_requests'
mean_values = df.groupby('benefit')[['served_requests', 'unserved_requests']].mean().reset_index()

# Plotting the line graph
plt.figure(figsize=(12, 8))
plt.plot(mean_values['benefit'], mean_values['served_requests'], label='Average Served Requests', marker='o', color = 'blue')
plt.plot(mean_values['benefit'], mean_values['unserved_requests'], label='Average Unserved Requests', marker='x', color = 'red')

# plt.title('Average Number of Served vs. Unserved Requests by Benefit')
plt.xlabel('Benefit (units)', fontsize=12)
plt.ylabel('Number of Requests', fontsize=12)
plt.legend()
# Adding grid for better readability
plt.grid(True)
# Ensuring layout is tight so everything fits without overlapping
plt.tight_layout()


plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/effect_b_on_sr_50.2_new.pdf')
