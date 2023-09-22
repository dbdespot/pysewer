# %%
import os

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file
# change the current working directory to the directory of the project
os.chdir(os.getenv("WORKSPACE_DIR"))
print(os.getcwd())

from operator import itemgetter

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import rasterio
from pyproj.crs import CRS
from shapely.geometry import LineString, Point, Polygon

import pysewer
from pysewer.helper import get_node_keys, remove_third_dimension

# %%

roads = pysewer.Roads("./tests/test_data/roads_clipped.shp")
buildings = pysewer.Buildings(
    "./tests/test_data/buildings_clipped.shp", roads_obj=roads
)
dem = pysewer.DEM("./tests/test_data/dem.tif")

# check the dem for nans
with rasterio.open("./tests/test_data/dem.tif") as src:
    dem_arr = src.read(1)  # reading the first band
    assert np.isnan(dem_arr).any() == False
nan_count = np.isnan(dem_arr).sum()
print(f"number of nan values: {nan_count}")

# check to see the crs are the same

print(roads.get_crs())
print(buildings.get_crs())
print(dem.get_crs.to_epsg())

# check the number of nans in the roads and buildings gdf
print(roads.get_gdf().isna().sum())
print(buildings.get_gdf().isna().sum())


modeldomain = pysewer.ModelDomain(
    dem="./tests/test_data/dem.tif",
    roads=roads.get_gdf(),
    buildings=buildings.get_gdf(),
)

unsimplified_g = modeldomain.create_unsimplified_graph(roads_gdf=roads.get_gdf())

g_connection = nx.Graph(unsimplified_g)

sub_graphs = list(
    (g_connection.subgraph(c).copy() for c in nx.connected_components(g_connection))
)

modeldomain.pump_penalty = 1000
nx.set_node_attributes(g_connection, True, "road_network")
nx.set_node_attributes(g_connection, "", "node_type")

modeldomain.connect_buildings(clustering="clustering")


edge_gdf = pysewer.get_edge_gdf(g_connection)
edge_gdf["closest_edge"] = edge_gdf.geometry
edge_gdf["closest_edge"] = edge_gdf.geometry.to_list()



print("done")
