# %%
import os

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file
# change the current working directory to the directory of the project
os.chdir(os.getenv("WORKSPACE_DIR"))
print(os.getcwd())

import geopandas as gpd
import matplotlib.pyplot as plt
import momepy
import networkx as nx
import pandas as pd

import pysewer

# %%

# import the required data from generating the sewer network
dem_file = "./data/first_test_area/dem.tif"
# dem_file = False
buildings_file = "./data/first_test_area/buildings.shp"
roads_file = "./data/first_test_area/roads.shp"
pipe_diameters = [0.2, 0.3, 0.4, 0.5, 0.8, 1, 2]
pressurized_diam = 0.2

# Lets look at the roads
roads = pysewer.Roads(roads_file)
# import the roads using geopandas
# roads_gdf = gpd.read_file(roads_file)
roads_gdf = roads.get_gdf()

# print the out the CRS of the roads
print(f"This is current CRS of the roads: ", {roads_gdf.crs})

roads_gdf.to_crs(epsg=32620, inplace=True)
# print the out the CRS of the roads
print(f"This is current CRS of the roads: ", {roads_gdf.crs})
roads_gdf.plot()


# lets look at the buildings
buildings = pysewer.Buildings(buildings_file, roads_obj=roads)

# print the out the CRS of the buildings
print(f"This is current CRS of the buildings: ", {buildings.get_gdf().crs})

# get the building gdf
buildings_gdf = buildings.get_gdf()
buildings_gdf.to_crs(epsg=32620, inplace=True)

# convert the geometry polygon to point
buildings_gdf["geometry"] = buildings_gdf["geometry"].centroid
buildings_gdf.plot()

# get the building cluster centers
building_cluster = buildings.cluster_centers(max_connection_length=20)
# plot the building cluster
building_cluster.plot()

# network_domain =  pysewer.ModelDomain(dem=dem_file, roads=roads_gdf, buildings=buildings_gdf)

# use momepy to convert the roads_gdf to a networkx.Graph
G = momepy.gdf_to_nx(roads_gdf, approach="primal")


# %%
f, ax = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)
roads_gdf.plot(color="#e32e00", ax=ax[0])
for i, facet in enumerate(ax):
    facet.set_title(("Streets", "Primal graph", "Overlay")[i])
    facet.axis("off")
nx.draw_networkx(
    G,
    {n: [n[0], n[1]] for n in list(G.nodes)},
    ax=ax[1],
    node_size=15,
    with_labels=False,
)
# Manually draw edges
for edge in G.edges():
    p1, p2 = edge
    x1, y1 = p1
    x2, y2 = p2
    ax[1].plot([x1, x2], [y1, y2], color='blue', linewidth=2)

roads_gdf.plot(color="#e32e00", ax=ax[2], zorder=-1)
# Manually draw edges
for edge in G.edges():
    p1, p2 = edge
    x1, y1 = p1
    x2, y2 = p2
    ax[2].plot([x1, x2], [y1, y2], color='blue', linewidth=2)
nx.draw(G, {n: [n[0], n[1]] for n in list(G.nodes)}, ax=ax[2], node_size=15)

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
    ax.plot([x1, x2], [y1, y2], color="blue", linewidth=2)

# Draw nodes
nx.draw(
    G,
    {n: [n[0], n[1]] for n in list(G.nodes)},
    ax=ax,
    node_size=15,
    with_labels=False,
    node_color="red",
)

# Optionally, zoom into a part of the graph
# ax.set_xlim([xmin, xmax])
# ax.set_ylim([ymin, ymax])


from shapely.ops import linemerge, nearest_points

from pysewer.helper import get_closest_edge_multiple, get_edge_gdf, get_node_gdf

G1 = nx.Graph(G)

sub_graphs = list((G1.subgraph(c).copy() for c in nx.connected_components(G1)))

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
    sub_graphs2 = list((G.subgraph(c).copy() for c in nx.connected_components(G)))

nx.set_node_attributes(G1, True, "road_network")
nx.set_node_attributes(G1, "", "node_type")

# %%
from pysewer.helper import get_closest_edge_multiple, get_edge_gdf, get_node_gdf

# connect to the buildings
buildings_points = buildings_gdf.geometry.tolist()
cluster_centers_gdf = buildings.cluster_centers(max_connection_length=30)
cluster_centers = cluster_centers_gdf.geometry.tolist()


# %%
print("done")
