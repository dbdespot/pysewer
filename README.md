<!-- SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
SPDX-License-Identifier: GPL-3.0-only -->
# pysewer

- [pysewer](#pysewer)
  - [Summary](#summary)
  - [Installation](#installation)
    - [Create a new conda environment and install GDAL](#create-a-new-conda-environment-and-install-gdal)
    - [Install pysewer via pip](#install-pysewer-via-pip)
  - [Input Data and data representation](#input-data-and-data-representation)
    - [Preprocessing](#preprocessing)
    - [Graph Attributes](#graph-attributes)
  - [Routing Solver](#routing-solver)
  - [Plotting](#plotting)
  - [Export](#export)
  - [License](#license)
- [How to contribute to pysewer?](#how-to-contribute-to-pysewer)
  - [Code of conduct](#code-of-conduct)
  - [How to cite?](#how-to-cite)

<!-- /TOC -->

## Summary

![Example of an automatically generated Sewer Network](notebooks/example_data/plots/modeldomain_pumps.png)

The aim of pysewer is to provide a framework automatically generate cost-efficient sewer network layouts on minimal data requirements. 

It is build around an algorithm for generation of viable sewer-network layouts. The approximated sewer network is represented by sources (households/buildings), potential pathways, and one or multiple sinks. The algorithm approximates the directed steinertree (the steiner arborescence) between all sources and the sink by using an repeated shortest path heuristic (RSPH).  



## Installation
Currently the installation is easiest managed via Anaconda. Anaconda 3 can be downloaded [here.](https://www.anaconda.com/products/individual)


### Create a new conda environment and install GDAL
First, we want to create a new environment in Anaconda. Therefor, we open Anaconda prompt and create a new Python 3.7 Environment and name it pysewer by running the following command:

```
conda create -n myenv python=3.10.6
```
We can then install GDAL, rasterio and fiona :

```
conda activate pysewer
conda install -c conda-forge gdal rasterio fiona
```
Note that the exact package version can be found in the [environment.yml](environment.yml) file.

### Install pysewer via pip
You can either get pysewer and install it using git and pip with:
```shell
git clone https://git.ufz.de/despot/pysewer_dev.git
cd pysewer
pip install .
# for the development version
python -m pip install -e .
```

## Input Data and data representation 

The following input data is required:
- A Digital Elevation Model (DEM)
- Point Data on Building locations
- Road Network Data


### Preprocessing

The main objective of sewer layout generation is to connect all buildings to a waste water treatment plant (WWTP) while keeping system cost low. The initial graph represents all potential sewer lines in our model domain. 

Preprocessing comes down to:

- "connecting" buildings to the street network
- clustering of buildings surpassing a predefined threshold 
- contracting the street network for more efficient graph traversal


After preprocessing, all relevant data is and stored as a MultiDiGraph to allow for asymmetric edge values (e.g. elevation profile and subsequently costs). 


### Graph Attributes
```
Node Attributes:
    "node_type": "building","wwtp"
    "elevation"
    "pumping_station": bool
    "lifting_station":bool
Edge Attributes:
    "geometry": detailed shapely line
    "length"
    "diameter"
    "pressurized": bool
    "profile"
    "needs_pump": bool
    "private_sewer":bool
    "weight": value representing arbitrary cost function
```

## Routing Solver

![Routing Animation](/notebooks/example_data/plots/rsph.gif)

The package comes with two solvers to find estimates for the underlying steiner tree problem (more specifically minimum steiner arboresence). 

- RSPH
- RSPH Fast
***

The *RSPH solver* iteratively connects the nearest unconnected node (in terms of distance and pump penalty) to the closest connected network node. The solver can account for multiple sinks and is therefore well suited to generate decentralized network scenarios.

The *RSPH Fast* solver derives the network by combining all shortest paths to a single sink. Faster, but only allows for a single sink. 



## Plotting
```python
info = pysewer.get_sewer_info(G)
info["Routing Solver"] = "RSPH"
info["Pump Penalty"] = test_model_domain.pump_penalty
fig,ax = pysewer.plot_model_domain(test_model_domain, plot_sewer=True,sewer_graph = G, info_table=info)
```

```python
pysewer.plot_sewer_attributes(test_model_domain,G,attribute="peak_flow",title="Peak Flow Estimation m³/s")
plt.show()
```

## Export
```python
sewer_network_gdf = pysewer.get_edge_gdf(G,detailed=True)
pysewer.export_sewer_network(sewer_network_gdf, "sewer_network.gpkg")
```
## License
GNU GPLv3-modified-UFZ. See [LICENSE](LICENSE) for details.

# How to contribute to pysewer?
Please check out how [Contributing](CONTRIBUTING.md) for on how to contribute to pysewer.

## Code of conduct
Please check out our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

## How to cite?
