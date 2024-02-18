import networkx as nx
import DataMappings as dict_map
import matplotlib.pyplot as plt


class Stop:
    def __init__(self, latitude, longitude, is_compulsory_stop, order, segment_h, is_origin, is_destination, node_id):
        self.latitude = latitude
        self.longitude = longitude
        self.is_compulsory_stop = is_compulsory_stop
        self.order = order
        self.segment_h = segment_h
        self.is_origin = is_origin
        self.is_destination = is_destination
        self.id = node_id


def initialize_stops():
    route_nodes = dict_map.route_nodes

    compulsory_stops_data = [node for node in route_nodes if node['is_compulsory_stop']]
    optional_stops_data = [node for node in route_nodes if not node['is_compulsory_stop']]

    compulsory_stops = [
        Stop(node['latitude'], node['longitude'], node['is_compulsory_stop'], node['order'], node['segment_h'],
             node['is_origin'], node['is_destination'], node['node_id']) for node
        in compulsory_stops_data]

    optional_stops = [
        Stop(node['latitude'], node['longitude'], node['is_compulsory_stop'], node['order'], node['segment_h'],
             node['is_origin'], node['is_destination'], node['node_id']) for node
        in optional_stops_data]

    return compulsory_stops, optional_stops


def build_graph(compulsory_stops: list, optional_stops: list) -> nx.Graph:
    """
    Function to build the graph for the DAS problem
    :param compulsory_stops: list of compulsory stops
    :param optional_stops: list of optional stops
    :return: graph
    """

    # Generate an empty directed networkx graph for each segment
    graph_for_segment = [nx.DiGraph() for i in range(len(dict_map.bounds) - 1)]

    for n in range(len(graph_for_segment)):
        graph = graph_for_segment[n]

        # Add all relevant nodes to the graph
        # Add the two respective compulsory stops to the segment graph
        for node in [node for node in compulsory_stops if n + 1 in node.segment_h]:
            graph.add_node(node, pos=(node.latitude, node.longitude), order=node.order,
                           segment_h=node.segment_h, is_origin=node.is_origin, is_destination=node.is_destination,
                           is_compulsory_stop=True, id=node.id)

        # Add all optional stops to the segment graph
        for opt_node in [opt_node for opt_node in optional_stops if opt_node.segment_h[0] == n + 1]:
            graph.add_node(opt_node, pos=(opt_node.latitude, opt_node.longitude), order=opt_node.order,
                           segment_h=opt_node.segment_h, is_origin=opt_node.is_origin,
                           is_destination=opt_node.is_destination,
                           is_compulsory_stop=False, id=node.id)

        # Add all relevant arcs to it
        for i in graph.nodes():
            for j in graph.nodes():
                if i != j:
                    graph.add_edge(i, j, weight=dict_map.distance_matrix[i.order][j.order],
                                   time=dict_map.time_matrix[i.order][j.order],
                                   segment=n + 1)

    # Join all segment graphs to one complete graph
    complete_graph = nx.compose_all(graph_for_segment)

    return complete_graph


def draw_graph(graph: nx.Graph):
    fig, ax = plt.subplots()

    node_pos = {node: (node.latitude, node.longitude) for node in graph.nodes()}

    num_segments = len([node for node in graph.nodes if node.is_compulsory_stop])

    cmap = plt.cm.get_cmap('tab10', num_segments)

    color_mapping = {}
    segment_colors = [cmap(i) for i in range(num_segments)]

    for node in graph.nodes():
        segment = node.segment_h if isinstance(node.segment_h, int) else node.segment_h[0]
        if segment not in color_mapping:
            color_mapping[segment] = segment_colors.pop(0)
        nx.draw_networkx_nodes(graph, pos=node_pos, nodelist=[node], node_color=color_mapping[segment],
                               node_size=200, ax=ax)

    for edge in graph.edges():
        nx.draw_networkx_edges(graph, pos=node_pos, edgelist=[edge], edge_color='black', ax=ax)

    plt.show()


def main():
    comp_stps, opt_stps = initialize_stops()
    graph = build_graph(comp_stps, opt_stps)
    return graph
    # test graph by drawing it
    # draw_graph(build_graph(comp_stps, opt_stps))
    # return graph

    # test graph
    # G = build_graph(comp_stps, opt_stps)
    # print(G.nodes)
    # count nodes in G
    # print(G.number_of_nodes())
    # edges in G
    # print(G.edges)
    # count edges in G
    # print(G.number_of_edges())


if __name__ == '__main__':
    main()
