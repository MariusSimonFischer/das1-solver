import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file into a DataFrame
file_path = '/Bachelor_Thesis_Code/Computational_Results_old_tw/Sensitivity Analysis/data/all_ben_wd.csv'
data = pd.read_csv(file_path)

# Box Plot for the Effect on Requests Served
plt.figure(figsize=(10, 6))
sns.boxplot(x='percentage_of_compulsory_stops', y='served_requests', data=data, color='k', palette=['0.75', '0.5', '0.25'])
#plt.title('Effect of Compulsory Stops Percentage on Requests Served')
plt.xlabel('Percentage of Compulsory Stops', fontsize=12)
plt.ylabel('Number of Requests Served', fontsize=12)

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results/Sensitivity Analysis/results/varying_compulsory_stops_on_requests.pdf')

