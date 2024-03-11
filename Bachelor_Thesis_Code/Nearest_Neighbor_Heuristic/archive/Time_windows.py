import data_mappings as dict_map
from math import radians, sin, cos, sqrt, atan2

compulsory_stops = []
coordinate_dict = []
time_windows = []


def reduce_to_compulsory_stops():
    """

    """
    global compulsory_stops
    compulsory_stops = []
    for node in dict_map.route_nodes:
        if node['is_compulsory_stop']:
            compulsory_stops.append(node)
    return compulsory_stops


def get_coordinates_between_stops():
    global coordinate_dict
    coordinate_dict = []
    for i in range(len(compulsory_stops)):
        # check if current stop is the last stop
        if i == len(compulsory_stops) - 1:
            break
        else:
            current_stop = compulsory_stops[i]
            order_current_stop = current_stop["order"]
            if i + 1 < len(compulsory_stops):
                next_stop = compulsory_stops[i + 1]
                order_next_stop = next_stop["order"]

            coordinate_dict.append({
                "segment_h": i,
                "lat1": current_stop["latitude"],
                "lon1": current_stop["longitude"],
                "order1": order_current_stop,
                "lat2": next_stop["latitude"],
                "lon2": next_stop["longitude"],
                "order2": order_next_stop
            })
    return coordinate_dict


def calculate_time_windows():
    """
    Funktion, um die Zeitfenster für die direkte und indirekte Strecke zwischen den Stops zu berechnen
    :return:
    """
    global time_windows
    time_windows = []
    for entry in coordinate_dict:
        # Berechnung der Distanz zwischen den aktuellen und nächsten Koordinaten in km
        distance = dict_map.distance_matrix[entry["order1"]][entry["order2"]]

        # Annahme: Geschwindigkeit in km/h (zum Beispiel 30 km/h)
        speed = 30  # in km/h
        time_taken = distance / speed  # Zeit = Entfernung / Geschwindigkeit
        # time_taken in Minuten
        time_taken = time_taken * 60

        time_window = {
            "segment_h": entry["segment_h"],
            "distance": distance,  # Entfernung zwischen den Koordinaten
            "time_for_direct_path": time_taken,  # Geschätzte Zeit zwischen den Stops in Minuten für direkt Strecke
            "time_for_indirect_path": time_taken * 1.5  # Zeitfenster für indirekte Strecke
        }
        time_windows.append(time_window)
    return time_windows


def main():
    reduce_to_compulsory_stops()
    print("compulsory_stops: " + str(compulsory_stops))
    print("Amount of compulsory stops in the data: " + str(len(compulsory_stops)))

    get_coordinates_between_stops()
    # print(coordinate_dict)

    calculate_time_windows()
    # print(time_windows)
    # print(len(time_windows))


if __name__ == "__main__":
    main()
