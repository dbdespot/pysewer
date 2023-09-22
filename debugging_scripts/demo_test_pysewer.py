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
from pysewer.helper import remove_third_dimension
import pandas as pd
import momepy

# %%

# import the required data from generating the sewer network 
###### Create SewerNetwork Object from input Data
dem_file = "./example_data/1_DEM/dem_10m1.tif"
buildings_file = "./example_data/2_Buildings/buildings_projected.shp"
roads_file = "./example_data/3_Roads/roads_projected.shp"
sink_coordinates = (691000, 2554600)
pipe_diameters = [0.2, 0.3, 0.4, 0.5, 0.8, 1, 2]
pressurized_diam = 0.2

dem = pysewer.DEM(dem_file)
print(f"This is current CRS of the dem: ", {dem.get_crs()})
# change dem crs to epsg 32620


# Lets look at the roads 
roads = pysewer.Roads(roads_file)
# import the roads using geopandas 
roads_gdf = gpd.read_file(roads_file)
# roads_gdf = roads.get_gdf()


# print the out the CRS of the roads
print(f"This is current CRS of the roads: ", {roads_gdf.crs})

roads_gdf.to_crs(crs=dem.get_crs(), inplace=True)
# print the out the CRS of the roads
print(f"This is current CRS of the roads: ", {roads_gdf.crs})
roads_gdf.plot()


# lets look at the buildings
buildings = pysewer.Buildings(buildings_file, roads_obj=roads)

# print the out the CRS of the buildings
print(f"This is current CRS of the buildings: ", {buildings.get_gdf().crs})

# get the building gdf 
# buildings_gdf = buildings.get_gdf()
# import the buildings using geopandas
buildings_gdf = gpd.read_file(buildings_file)
# change to crs to the dem crs
buildings_gdf.to_crs(crs=dem.get_crs(), inplace=True)

# convert the geometry polygon to point
# buildings_gdf["geometry"] = buildings_gdf["geometry"].centroid
buildings_gdf.plot()

# get the building cluster centers 
building_cluster = buildings.cluster_centers(max_connection_length=20)
#plot the building cluster
building_cluster.plot()


# %%
# network_domain =  pysewer.ModelDomain(dem=dem_file, roads=roads_gdf, buildings=buildings_gdf, clustering="sewquential")
network_domain =  pysewer.ModelDomain(dem=dem_file, roads=roads_file, buildings=buildings_file)

network_domain.set_sink_lowest()
network_domain.add_sink((690500,2557000))

fig,ax = pysewer.plot_model_domain(network_domain,plot_connection_graph=True,hillshade=False)

# %%
connection_graph = network_domain.generate_connection_graph()
layout = pysewer.rsph_tree(connection_graph, network_domain.get_sinks(),"building") 

fig,ax = pysewer.plot_model_domain(network_domain, plot_sewer=True, sewer_graph = layout)

print("done!!")