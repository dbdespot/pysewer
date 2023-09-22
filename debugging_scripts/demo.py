# %%
import os 
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file
# change the current working directory to the directory of the project 
os.chdir(os.getenv("WORKSPACE_DIR"))
print(os.getcwd())
import geopandas as gpd
import matplotlib.pyplot as plt
import momepy
import networkx as nx

import pysewer

# %%
###### Create SewerNetwork Object from input Data
dem_file = "./example_data/1_DEM/dem_10m1.tif"
buildings_file = "./example_data/2_Buildings/buildings_projected.shp"
roads_file = "./example_data/3_Roads/roads_projected.shp"
sink_coordinates = (691000, 2554600)
pipe_diameters = [0.2, 0.3, 0.4, 0.5, 0.8, 1, 2]
pressurized_diam = 0.2


# Inspect the data input components
# roads
roads = pysewer.Roads(roads_file)
roads_gdf = roads.get_gdf()
# set the roads crs to none 
roads_gdf.crs = None
# print the out the CRS of the roads
print(f"This is current CRS of the roads: ", {roads_gdf.crs})
roads_gdf.plot()

# buildings
buildings = pysewer.Buildings(buildings_file, roads_obj=roads)
buildings_gdf = buildings.get_gdf()
buildings_gdf.plot()

# buildings cluster
building_cluster = buildings.cluster_centers(max_connection_length=30)
building_cluster.plot()

# graph created by converting the roads to a networkx graph using momempy
G = momepy.gdf_to_nx(roads_gdf, approach="primal")
# print out the basic statistics of the graph
print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Number of self-loops: {nx.number_of_selfloops(G)}")

#create graph by converting the roads shapefile to the networkx graph using the networkx read_shp function
G_nx = nx.read_shp(roads_file, simplify=False)
print(f"Number of nodes: {G_nx.number_of_nodes()}")
print(f"Number of edges: {G_nx.number_of_edges()}")
print(f"Number of self-loops: {nx.number_of_selfloops(G_nx)}")


# try creating an unsimplified graph

def create_unsimplified_graph(roads_gdf):
    # Initialize an empty undirected graph
    G_unsimplified = nx.Graph()

    # Populate the graph with nodes and edges from the GeoDataFrame
    for index, row in roads_gdf.iterrows():
        line = row['geometry']
        road_attrs = row.drop('geometry').to_dict()  # All attributes other than 'geometry'

        for i in range(len(line.coords) - 1):
            start_point = line.coords[i]
            end_point = line.coords[i + 1]

            # Add edge to the graph
            G_unsimplified.add_edge(start_point, end_point, **road_attrs)    

    return G_unsimplified

G_unsimplified = create_unsimplified_graph(roads_gdf)

print(f"Number of nodes: {G_unsimplified.number_of_nodes()}")
print(f"Number of edges: {G_unsimplified.number_of_edges()}")
print(f"Number of self-loops: {nx.number_of_selfloops(G_unsimplified)}")
# %%
import networkx as nx
import matplotlib.pyplot as plt

def plot_graph_on_roads(G, roads_gdf):
    f, ax = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)
    roads_gdf.plot(color="#e32e00", ax=ax[0])
    for i, facet in enumerate(ax):
        facet.set_title(("Streets", "Primal graph", "Overlay")[i])
        facet.axis("off")
    # Draw the graph with nodes and edges (MODIFIED)
    nx.draw(
        G,
        {n: [n[0], n[1]] for n in list(G.nodes)},
        ax=ax[1],
        node_size=15,
        with_labels=False,
        edge_color="blue",
        width=2,
    )
    for edge in G.edges():
        p1, p2 = edge
        x1, y1 = p1
        x2, y2 = p2
        ax[1].plot([x1, x2], [y1, y2], color='k', linewidth=2)

    # Overlay roads and graph (MODIFIED)
    roads_gdf.plot(color="#e32e00", ax=ax[2], zorder=-1)
    nx.draw(
        G,
        {n: [n[0], n[1]] for n in list(G.nodes)},
        ax=ax[2],
        node_size=15,
        with_labels=False,
        edge_color="k",
        width=2,
    )
    for edge in G.edges():
        p1, p2 = edge
        x1, y1 = p1
        x2, y2 = p2
        ax[2].plot([x1, x2], [y1, y2], color='k', linewidth=2)

    return f, ax


fig, ax = plot_graph_on_roads(G, roads_gdf)
fig, ax = plot_graph_on_roads(G_nx, roads_gdf)
fig, ax = plot_graph_on_roads(G_unsimplified, roads_gdf)
# %%
# Check if graph has edges
if G.edges:
    print(f"The graph has {len(G.edges)} edges.")
else:
    print("The graph has no edges.")

# Print out some node positions to check
node_positions = {n: [n[0], n[1]] for n in list(G.nodes)}
print("Some node positions:", list(node_positions.items())[:5])

# Draw only the NetworkX graph for debugging
plt.figure(figsize=(10, 10))
nx.draw_networkx(
    G,
    pos=node_positions,
    node_size=15,
    with_labels=False,
    edge_color="blue",
    width=2,
)
plt.title("Isolated NetworkX Graph")

# %%
# Manuualy draw edges
# Create subplots
f, ax = plt.subplots(1, 1, figsize=(12, 12))

# Manually draw edges
for edge in G.edges():
    p1, p2 = edge
    x1, y1 = p1
    x2, y2 = p2
    ax.plot([x1, x2], [y1, y2], color='blue', linewidth=2)

# Draw nodes
nx.draw(G, {n: [n[0], n[1]] for n in list(G.nodes)}, ax=ax, node_size=15, with_labels=False, node_color='red')

# Optionally, zoom into a part of the graph
# ax.set_xlim([xmin, xmax])
# ax.set_ylim([ymin, ymax])

# %%
from pysewer.helper import get_edge_gdf, get_node_gdf, get_closest_edge_multiple
from shapely.ops import linemerge, nearest_points


connecntion_graph =  nx.read_shp(roads_file, simplify=False)

G1 = nx.Graph(G)

sub_graphs = list(
            (
               G1.subgraph(c).copy()
                for c in nx.connected_components(G1)
            )
        )

while len(sub_graphs) > 1:
            # select one subgraph
            sg = sub_graphs.pop()
            G_without_sg = sub_graphs.pop()

            while len(sub_graphs) > 0:
                G_without_sg = nx.compose(G_without_sg, sub_graphs.pop())

            # get shortest edge between sg and G_withouto_sg:
            sg_gdf = get_node_gdf(sg).unary_union
            G_without_sg_gdf = get_node_gdf(G_without_sg).unary_union
            connection_points = nearest_points(sg_gdf, G_without_sg_gdf)

            # add edge
            G.add_edge(
                (connection_points[0].x, connection_points[0].y),
                (connection_points[1].x, connection_points[1].y),
                road_network=True,
            )
            # get updated subgraph list
            sub_graphs2 = list(
                (G.subgraph(c).copy() for c in nx.connected_components(G))
            )

nx.set_node_attributes(G1, True, "road_network")
nx.set_node_attributes(G1, "", "node_type")

# %%
from pysewer.helper import get_edge_gdf, get_node_gdf, get_closest_edge_multiple
# connect to the buildings 
buildings_points  = buildings_gdf.geometry.tolist()
cluster_centers_gdf = buildings.cluster_centers(max_connection_length=30)
cluster_centers = cluster_centers_gdf.geometry.tolist()

# print the number of nans in the gdf 
print(f"Number of nans in the gdf: {cluster_centers_gdf.isna().sum().sum()}")

# Initialize Model Domain Object
# test_model_domain = pysewer.ModelDomain(dem=dem_file,buildings=buildings_file,roads=roads_file, clustering="other")
# #Set one Sink at lowest network node
# test_model_domain.set_sink_lowest()
# #Create connection graph
# connection_graph = test_model_domain.generate_connection_graph()
# Routing
# layout = pysewer.rsph_tree(connection_graph,test_model_domain.get_sinks(),"building")
# #Hydraulic Optimization
# sewer = pysewer.estimate_peakflow(layout,inhabitants_dwelling=6,daily_wastewater_person=0.250)
# sewer = pysewer.calculate_hydraulic_parameters(sewer,diameters = pipe_diameters,pressurized_diameter=pressurized_diam,include_private_sewer=True,roughness = 0.012,sinks = test_model_domain.get_sinks())
# %%
print("done")
