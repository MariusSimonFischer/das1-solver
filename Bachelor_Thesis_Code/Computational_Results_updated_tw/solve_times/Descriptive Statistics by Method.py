import pandas as pd

def load_data(file_path):
    """Lädt CSV-Daten."""
    return pd.read_csv(file_path)

def calculate_descriptive_stats(df, column_name):
    """Berechnet deskriptive Statistiken für eine gegebene Spalte."""
    stats = {
        "count": len(df),
        "mean": df[column_name].mean(),
        "std": df[column_name].std(),
        "min": df[column_name].min(),
        "25%": df[column_name].quantile(0.25),
        "50%": df[column_name].median(),
        "75%": df[column_name].quantile(0.75),
        "max": df[column_name].max(),
    }
    stats["iqr"] = stats["75%"] - stats["25%"]
    stats["range"] = stats["max"] - stats["min"]
    return stats

# Pfad zu Ihren CSV-Dateien anpassen
file_paths = {
    "gurobi": "/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/solve_times/data/solve_times_new_tw_gurobi1.csv",
    "gh": "/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/solve_times/data/solving_times_new_tw_gh1.csv",
    "nnh": "/Users/mariusfischer/Desktop/Bachelor Thesis/Business Analytics & Intelligent Systems/Coding/Code/Bachelor_Thesis_Code/Computational_Results_updated_tw/solve_times/data/solving_times_new_tw_nnh1.csv",
}

# Lädt Daten
dfs = {method: load_data(path) for method, path in file_paths.items()}

# Berechnet Statistiken für Lösungszeiten und Zielwerte
stats_solve_time = {method: calculate_descriptive_stats(df, "solve_time") for method, df in dfs.items()}
stats_obj_val = {method: calculate_descriptive_stats(df, "obj_val") for method, df in dfs.items()}

print("Statistiken für Lösungszeiten:", stats_solve_time)
print("\nStatistiken für Zielwerte:", stats_obj_val)
