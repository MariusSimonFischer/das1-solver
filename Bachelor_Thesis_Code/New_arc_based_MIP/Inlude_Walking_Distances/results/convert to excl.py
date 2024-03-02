import pandas as pd


# CSV-Datei laden
df = pd.read_csv('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/New_arc_based_MIP/Inlude_Walking_Distances/results/several_wd_b.csv')


# erstelle excel file
df.to_excel('/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/New_arc_based_MIP/Inlude_Walking_Distances/results/several_wd_b.xlsx', index=False)

