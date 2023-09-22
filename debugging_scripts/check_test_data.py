# %%
import os 
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file
# change the current working directory to the directory of the project 
os.chdir(os.getenv("WORKSPACE_DIR"))
print(os.getcwd())

import pysewer
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
from pysewer.helper import remove_third_dimension, get_node_keys
from shapely.geometry import LineString, Point, Polygon
from operator import itemgetter
from pysewer.optimization import mannings_equation, estimate_peakflow, calculate_hydraulic_parameters
from pysewer.routing import rsph_tree, find_rsph_path

import pandas as pd

# %%
sink_coordinates = (691350,2553250)
dem = "./tests/test_data/dem.tif"  
buildings = "./tests/test_data/buildings_clipped.shp"
roads = "./tests/test_data/roads_clipped.shp"

# %%
roads_gdf = gpd.read_file(roads)
roads_gdf
# %%
buildings_gdf = gpd.read_file(buildings)
buildings_gdf.info()
# %%
buildings_gdf.loc[:, "Name"].unique()
# %%
buildings_gdf["geometry"] =  [remove_third_dimension(x) for x in buildings_gdf["geometry"]]
if "MultiPoint" in buildings_gdf.geometry.type.unique():
            convert = lambda MultiP: Point(MultiP.geoms[0].x, MultiP.geoms[0].y) if MultiP.geom_type == "MultiPoint" else MultiP
            buildings_gdf["geometry"] = buildings_gdf["geometry"].apply(convert)

# %%
buildings_gdf
# %%
model_domain = pysewer.ModelDomain(dem,roads,buildings)
# %%
diameter = 0.5
slope = -0.01
roughness = 0.012

m = mannings_equation(diameter,roughness,slope)
m
# %%

# focus on the fixing the find_rsph_path function
model_domain.add_sink(sink_coordinates) 
connection_graph = model_domain.generate_connection_graph()


sewer_graph = nx.DiGraph(nx.create_empty_copy(connection_graph))
terminals = get_node_keys(connection_graph, field="node_type", value="building")
subgraph_nodes = [sink_coordinates]

terminals

# %%
if len(subgraph_nodes) == 1:
        subgraph_nodes = [sink_coordinates] + [sink_coordinates]
all_paths = dict(nx.all_pairs_dijkstra_path(connection_graph))
all_lengths = dict(nx.all_pairs_dijkstra_path_length(connection_graph))


# %%
terminal_distances = []
closest_tree_node = []
for terminal in terminals:
    if any(node not in all_lengths[terminal] for node in subgraph_nodes):
        missing_nodes = [node for node in subgraph_nodes if node not in all_lengths[terminal]]
        print(f"Terminal {terminal} missing distances to nodes: {missing_nodes}.")
        continue
    # get distances from the terminal node to all nodes in the subgraph
    distances  =  [all_lengths[terminal][node] for node in subgraph_nodes]
    min_dist = min(distances)
    tree_node = subgraph_nodes[distances.index(min_dist)]
    terminal_distances.append(min_dist)
    closest_tree_node.append(tree_node)

# %%
min_dist_global = min(terminal_distances)
result_index = terminal_distances.index(min_dist_global)
closest_terminal = terminals[result_index]
tree_node = closest_tree_node[result_index]

# %%
terminal_distances
# %%
if tree_node not in all_paths[closest_terminal]:
        raise ValueError(
            f"No recorded path from {closest_terminal} to {tree_node} in the all_paths dictionary."
        )
paths1 = all_paths[closest_terminal][tree_node]
paths1

# %%
# the rsph path is the shortest path from the closest terminal to the tree node seems to work. 
# now the check the rsph_tree function

path = find_rsph_path(
            connection_graph, subgraph_nodes, terminals, all_paths, all_lengths
        )
path


# %%

# add edges of path to sewer graph while keeping edge attributes
nx.add_path(sewer_graph, path)

edgesinpath = zip(path[0:], path[1:])
for e in edgesinpath:
    nx.set_edge_attributes(
        sewer_graph,
        {(e[0], e[1]): connection_graph.get_edge_data(e[0], e[1])[0]}
    )
subgraph_nodes = subgraph_nodes + path[1:-1]

print(edgesinpath)
print(subgraph_nodes)
                
sewer_graph = terminals.remove(path[0])
# %%
skip_nodes = []
sewer_graph = nx.DiGraph(nx.create_empty_copy(connection_graph))
terminals = get_node_keys(connection_graph, field="node_type", value="building")
terminals = [n for n in terminals if n not in skip_nodes]

subgraph_nodes = [sink_coordinates]

if len(subgraph_nodes) == 1:
        subgraph_nodes = [sink_coordinates] + [sink_coordinates]
all_paths = dict(nx.all_pairs_dijkstra_path(connection_graph))

while len(terminals) > 0:
        path = find_rsph_path(
            connection_graph, subgraph_nodes, terminals, all_paths, all_lengths
        )

        # add edges of path to sewer graph while keeping edge attributes
        nx.add_path(sewer_graph, path)

        edgesinpath = zip(path[0:], path[1:])
        for e in edgesinpath:
            nx.set_edge_attributes(
                sewer_graph,
                {(e[0], e[1]): connection_graph.get_edge_data(e[0], e[1])[0]},
            )
        subgraph_nodes = subgraph_nodes + path[1:-1]
        terminals.remove(path[0])
# %%

layout = rsph_tree(connection_graph, sink_coordinates)

sewer_g = estimate_peakflow(layout,inhabitants_dwelling=6,daily_wastewater_person=250)


# %%
# new problem, the calculate_hydraulic_parameters function is not working
# the reverse_bfs is casusing a problem 
# networkx.exception.NetworkXError: nbunch is not a node or a sequence of nodes.
# ensure that sinks is a list of nodes

sewer_g_diameter = calculate_hydraulic_parameters(layout, sinks= [sink_coordinates], pressurized_diameter = 0.2,diameters =[0.2,.3,.4,.5,1,2],roughness = 0.012)

print("done1")