import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the first CSV file
df_no_optional_stops = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/comp_no_opt_stops_updated_250.csv')
# Load the second CSV file
df_with_optional_stops = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/data/comp_with_opt_stops_updated_250.csv')

# Add a column to each DataFrame to distinguish between them
df_no_optional_stops['Type'] = 'Static Bus Line'
df_with_optional_stops['Type'] = 'Adaptive Bus Line'

# Combine the two datasets for plotting
df_combined_scatter = pd.concat([
    df_no_optional_stops[['requests', 'served_requests', 'Type']],
    df_with_optional_stops[['requests', 'served_requests', 'Type']]
])

# Create the scatter plot with trend lines
sns.lmplot(x='requests', y='served_requests', hue='Type', data=df_combined_scatter,
           aspect=1.5, ci=None, markers=["o", "x"], palette="Set1")

#plt.title('Scatter Plot of Requests vs. Served Requests with Trend Lines')
plt.xlabel('Total Requests')
plt.ylabel('Served Requests')
plt.grid(True)


# Save the plot as a PDF file
plt.savefig('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/sensitivity_analysis/results/comp_trend_line_updated_250.pdf')
