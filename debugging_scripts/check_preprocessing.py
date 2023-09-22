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

import pandas as pd

# %%
def connection_graph():
    sink_coordinates = [(691350,2553250)]
    dem = "./tests/test_data/dem.tif"  
    buildings = "./tests/test_data/buildings_clipped.shp"
    roads = "./tests/test_data/roads_clipped.shp"
    model_domain = pysewer.ModelDomain(dem,roads,buildings)
    model_domain.add_sink(sink_coordinates)
    connection_graph = model_domain.generate_connection_graph()
    return connection_graph

connection_graph = connection_graph()

# %%
def test_edge_data_needs_pump(connection_graph):
    test_u = (691535.5977087952, 2553057.6150246616)
    test_v = (691567.7330147347, 2552952.9508892866)
    assert connection_graph[test_u][test_v][0]['needs_pump'] == False
    test_u = (691368.1738897682, 2553245.14452104)
    test_v = (691382.4957703799, 2553166.3549703807)
    assert connection_graph[test_u][test_v][0]['needs_pump'] == True
# %%
test_u = (691535.5977087952, 2553057.6150246616)
test_v = (691567.7330147347, 2552952.9508892866)
# check if needs_pumpis False
assert connection_graph[test_u][test_v][0]['needs_pump'] == False

test_u = (691384.1703000003, 2553067.1856999993)
test_v = (691386.9481000002, 2553059.71885)
assert connection_graph[test_u][test_v][0]['needs_pump'] == True

# %%
sink_coordinates = [(691350,2553250)]
wwtp_loc = pysewer.get_node_keys(connection_graph,field="node_type",value= "wwtp")[0]
for b in pysewer.get_node_keys(connection_graph,field="node_type",value= "building"):
    assert nx.has_path(connection_graph,b,wwtp_loc)

# %%

test_u = (691384.1703000003, 2553067.1856999993)
test_v = (691386.9481000002, 2553059.71885)

# assert connection_graph[test_u][test_v][0]['weight'] == 1000*79.66807500749309

# default pump penalty is 1000
assert connection_graph[test_u][test_v][0]['weight'] ==  7966.807500749309

# set pump penalty to 1
model_domain = pysewer.ModelDomain("./tests/test_data/dem.tif","./tests/test_data/roads_clipped.shp","./tests/test_data/buildings_clipped.shp")
model_domain.add_sink([(691350,2553250)])
model_domain.set_pump_penalty(1)
connection_graph= model_domain.generate_connection_graph()
assert connection_graph[test_u][test_v][0]['weight'] ==  7966.807500749309/1000




# %%
print("done!")