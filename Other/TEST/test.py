import json
import pandas as pd

"""
Load a JSON file into a pandas dataframe

Args:
    filename (str): The name of the JSON file to be loaded.

    Returns:
    dataframe: The dataframe containing the data from the JSON file.

def load_json_via_pandas(filename):
    return pd.read_json(filename)
"""

def load_json(filename):
    """
    Load a JSON file into a dictionary.

    Args:
    filename (str): The name of the JSON file to be loaded.

    Returns:
    dict: The dictionary containing the data from the JSON file.
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {filename}.")
        return None


def main():
    print("Test")
    path = "../Old_data/data/output_55_07_59_30_0.json"
    data = load_json(path)
    building_pairs = data["sampled_building_pairs"]

    print(building_pairs[0])


if __name__ == "__main__":
    main()