import json


def load_json(filename):
    """
    Load a JSON file into a dictionary.
    Args: filename (str): The name of the JSON file to be loaded.
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
    # Load the JSON file into a dictionary
    path = '../jsons/jsons_updated_new_tw/jsons_new_tw/55_15_58_00_0.2_200_200_0.json'
    data = load_json(path)

    """
    # If data is successfully loaded, print part of the dictionary - this is for testing purposes only.
    if data:
        # Extract a part of the dictionary to show
        # Here we show only the first few key-value pairs for demonstration
        part_of_data = dict(list(data.items())[:5])
        print("Part of the loaded dictionary:")
        print(json.dumps(part_of_data, indent=4))
    
    # Testing data for 100% of compulsory stops

    # print(len(data['time_windows']))

    # print(len(data['route_nodes']))

    # print(data['route_nodes'])

    list = []
    for id in data['route_nodes']:
        if id['node_id'] not in list:
            list.append(id['node_id'])

    print(len(list))
    """

    return data


# Call the main function
if __name__ == "__main__":
    main()
