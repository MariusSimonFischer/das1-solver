import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the first CSV file
df_no_optional_stops = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/comp_no_opt_stops_updated.csv')
# Load the second CSV file
df_with_optional_stops = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/comp_with_opt_stops.csv')

# Create a combined DataFrame for comparison
df_combined = pd.DataFrame({
    "Static": df_no_optional_stops['served_requests'],
    "Adaptive": df_with_optional_stops['served_requests']
})

# Melt the DataFrame for easier plotting with seaborn
df_melted = df_combined.melt(var_name='Dataset', value_name='Served Requests')

# Create a boxplot comparing the two datasets
plt.figure(figsize=(10, 6))
sns.boxplot(x='Dataset', y='Served Requests', data=df_melted, color='k', palette=['0.75', '0.5', '0.25'])
# plt.title('Comparison of Served Requests With and Without Optional Stops')
plt.ylabel('Served Requests')
plt.xlabel('Type of Bus Line')
plt.xticks(rotation=0)
plt.tight_layout()
# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/comp_box_plot_updated_500_new.pdf')


