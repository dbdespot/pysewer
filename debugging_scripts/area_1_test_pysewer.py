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


import pandas as pd
import momepy

# %%

# import the required data from generating the sewer network 
dem_file = "./data/first_test_area/dem.tif"
#dem_file = False
buildings_file = "./data/first_test_area/buildings.shp"
roads_file = "./data/first_test_area/roads.shp"
pipe_diameters = [0.2,0.3,0.4,0.5,0.8,1,2]
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
# buildings_gdf.plot()

# get the building cluster centers 
building_cluster = buildings.cluster_centers(max_connection_length=20)
#plot the building cluster
building_cluster.plot()


# %%
network_domain =  pysewer.ModelDomain(dem=dem_file, roads=roads_gdf, buildings=buildings_gdf)

network_domain.set_sink_lowest()
print(network_domain.get_sinks())

fig,ax = pysewer.plot_model_domain(network_domain,plot_connection_graph=True,hillshade=True)
plt.show()

print("done!!")