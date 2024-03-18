import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file into a DataFrame
file_path = '/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/varying_comp_stops.csv'
data = pd.read_csv(file_path)



# Box Plot for the Effect on Objective Value
plt.figure(figsize=(10, 6))
sns.boxplot(x='percentage_of_compulsory_stops', y='obj_val', data=data, color='k', palette=['0.75', '0.5', '0.25'])
#plt.title('Effect of Compulsory Stops Percentage on Objective Value')
plt.xlabel('Percentage of Compulsory Stops')
plt.ylabel('Objective Value (units)')

# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/varying_cs_on_objval_new.pdf')

