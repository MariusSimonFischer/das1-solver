import Time_windows as tw

# start = 0
bounds = []


def calculate_a_and_b_bounds():
    """
    Function to calculate the a and b bounds
    a_nound of prenode + time for indirect path + 1
    b_bound of prenode + time for indirect path + 2
    :return:
    """
    compulsory_stops = tw.reduce_to_compulsory_stops()

    global bounds
    bounds = []

    for i in range(len(compulsory_stops)):
        if i == 0:
            bounds.append({'a': 0, 'b': 0})
        else:
            time_windows = tw.calculate_time_windows()
            value_a = bounds[i - 1]['a'] + time_windows[i - 1]['time_for_direct_path']
            value_b = bounds[i - 1]['b'] + time_windows[i - 1]['time_for_indirect_path']

            bounds.append({'a': value_a, 'b': value_b})
    return bounds


def main():
    calculate_a_and_b_bounds()


if __name__ == '__main__':
    main()
