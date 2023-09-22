import geopandas as gpd
import matplotlib.pyplot as plt
import momepy
import networkx as nx
from shapely.geometry import LineString
import pandas as pd 


data = {
    'road_id': [1, 2, 3, 4, 5],
    'speed_limit': [30, 40, 30, 40, 50],
    'road_type': ['residential', 'highway', 'residential', 'highway', 'motorway']
}
df = pd.DataFrame(data)

geometry = [
    LineString([(0, 0), (0, 1)]),
    LineString([(0, 1), (1, 1)]),
    LineString([(1, 1), (1, 0)]),
    LineString([(1, 0), (0, 0)]),
    LineString([(0, 0), (1, 1)])
]

gdf = gpd.GeoDataFrame(df, geometry=geometry)

# cpnvert gdf to shape file 
gdf.to_file("./data/test.shp")



# now create the graph using nx.read_shp
G_nx = nx.read_shp("./data/test.shp", simplify=False)
# print out the basic statistics of the graph
print(f"Number of nodes: {G_nx.number_of_nodes()}")
print(f"Number of edges: {G_nx.number_of_edges()}")
print(f"Number of self-loops: {nx.number_of_selfloops(G_nx)}")

# now create the graph using momepy
G = momepy.gdf_to_nx(gdf, approach="primal")
# print out the basic statistics of the graph
print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Number of self-loops: {nx.number_of_selfloops(G)}")



print("done")