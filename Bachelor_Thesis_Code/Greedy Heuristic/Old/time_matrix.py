import data_mappings as dict_map

time_matrix = []


# Function to calculate the time matrix between all nodes
def calculate_time_matrix():
    """
    Function to calculate the time matrix between all nodes
    :return:
    """
    global time_matrix
    time_matrix = dict_map.distance_matrix

    for i in range(len(dict_map.distance_matrix)):
        for j in range(len(dict_map.distance_matrix[i])):
            time_matrix[i][j] = (dict_map.distance_matrix[i][j] / 30 * 60)

    return time_matrix


def main():
    calculate_time_matrix()


if __name__ == "__main__":
    main()
