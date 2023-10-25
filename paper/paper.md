---
title: "Pysewer: A Python Library for Sewer Network Generation in Data Scarce Regions"
tags:
  - Python
  - sewer network
  - wastewater
  - infrastructure
  - planning
  - design
  - graph theory
authors:
  - name: Moritz Sanne
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Ganbaatar Khurelbaatar
    orcid: 0000-0002-2430-1612
    affiliation: 1
  - name: Daneish Despot
    corresponding: true
    orcid: 0000-0002-8980-5651
    affiliation: 1
  - name: Manfred van Afferden
    affiliation: 1
  - name: Jan Friesen
    orcid: 0000-0003-0454-0437
    affiliation: 1

affiliations:
  - name: Centre for Environmental Biotechnology, Helmholtz Centre for Environmental Research GmbH – UFZ, Permoserstraße 15 | 04318 Leipzig, Germany
    index: 1
  - name: Europace AG, Berlin, Germany
    index: 2
date: 22 October 2023
bibliography: paper.bib
---

# Summary

Pysewer is a network generator for sewer networks originally designed for rural settlements in emerging countries with little or no wastewater infrastructure. The network generation prioritises gravity flow in order to avoid pumping – which can be a source of failure and high maintenance – where possible. The network dimensioning is based on dry-weather flow.

Based on a few data sources, pysewer generates a complete network based on roads, building locations, and elevation data. Global water consumption and population assumptions are included to dimension the sewer diameter. Results are fully-connected sewer networks that connect all buildings to one or several predefined wastewater treatment plant (WWTP) locations. By default, the lowest point in the elevation data is set as the WWTP. The resulting network contains sewer diameters, building connections, as well as lifting stations or pumping stations with pressurised pipes where necessary.

# Statement of Need

The sustainable management of water and sanitation has been defined as one of the UN’s sustainable development goals: SDG #6 [@unwaterSustainableDevelopment2018]. As of 2019, SDG 6 might not be reached in 2030 despite the progress made, which means that more than half of the population still lacks safely managed sanitation [@unwaterSustainableDevelopment2018].  
In order to identify optimal wastewater management at the settlement level, it is necessary to compare different central or decentral solutions. To achieve this, a baseline is required against which other scenarios can be compared [@vanafferdenNewapproach2015; @khurelbaatarDataReduced2021]. To this end, we developed pysewer – a tool that generates settlement-wide sewer networks, which connect all the buildings within the settlement boundary or the region of interest to one or more wastewater treatment plant locations.

Pysewer is a tool for data-scare environments using only few data and global assumptions – thus enabling a transferability to a wide range of different regions. At the same time, a priori data sources can be substituted with high-resolution data and site-specific information such as local water consumption and population data.
The generated networks can then be exported (i.e., as a geopackage or shapefile) in order to utilise the results in preliminary planning stages, initial cost estimations, scenario development processes or for further comparison to decentral solutions where the network can be modified. The option to include several treatment locations also enables users to already plan decentralised networks or favour treatment locations (i.e., due to local demands or restrictions).

# Functionality and key features

Pysewer’s concept is built upon network science, where we combine algorithmic optimisation using graph theory with sewer network engineering design to generate a sewer network layout. In the desired layout, all buildings are connected to a wastewater treatment plant (WWTP) through a sewer network, which utilises the terrain to prioritise gravity flow in order to minimise the use of pressure sewers. Addressing the intricate challenge of generating sewer network layouts, particularly in data-scarce environments, is at the forefront of our objectives. Our approach, therefore, leans heavily towards utilising data that can be easily acquired for a specific area of interest. Thus, we deploy the following data as input to autonomously generate a sewer network, with a distinct prioritisation towards gravity flow.

1. Digital Elevation Model (DEM) – to derive the elevation profile and understand topographic details such as the lowest point (sinks) within the area of interest.
2. Existing road network data – Preferred vector data format in the form of `LineString` to map and utilise current infrastructure pathways.
3. Building locations – defined by x, y coordinate points, these points represent service requirement locations and identify the connection to the network.
4. Site-specific water consumption and population data – to plan/size hydraulic elements of the sewer network and estimate the sewage flow.  
   The core functionalities of pysewer include transforming the minimal inputs into an initial network graph—the foundation for the ensuing design and optimisation process; the generation of a gravity flow-prioritised sewer network—identifying the most efficient network paths and positions of the pump and lift stations where required; and the visualisation and exporting of the generated network—allowing visual inspection of the sewer network attributes and export of the generated sewer network. \autoref{fig:fig1} provides a visual guide of the distinct yet interconnected modules within pysewer.

![Pysewer's modular workflow\label{fig:fig1}](./media/figures/pysewer_module_new.png)

## Preprocessing and initial network generation

In the preprocessing module, the roads, buildings and the DEM must all be projected in the same projection (CRS) and must be in the form of a geopandas [@kelsey_jordahl_2020_3946761] data frame or a shapefile. `Roads`, `Buildings` and `DEM` classes are used to transform the raw data formats into the required format (i.e., geopandas data frame) to create the initial graph network (networkx, [@SciPyProceedings_11]), where nodes represent crucial points such as junctions or buildings and edges to simulate potential sewer lines. The following measures ensure that the initial layout aligns with the road network and that there is serviceability to all buildings within the area of interest:

- “connecting” buildings to the street network using the connect buildings method. This method adds nodes to the graph to connect the buildings in the network using the building points.
- Creation of “virtual roads”. Buildings which are not directly connected to the road network are connected by finding the closest edge to the building, which is then marked as the closest edge. The nodes are then disconnected from the edges and are added to the initial connection graph network.
- Contracting the street network for more efficient graph traversal.
- Setting of the collection point or Wastewater Treatment Plant (WWTP).By default, the lowest elevation point in the region of interest is set as the location of the WWTP. Users can manually define the location of the WWTP by using the `add_sink` method.

After preprocessing, all relevant data is stored as a `MultiDiGraph` to allow for asymmetric edge values (e.g., elevation profile and subsequently costs). \autoref{fig:fig2} demonstrates the required data, its preprocessing and the generation of the initial graph network.

![Pysewer preprocessing. Topographic map with the connection graph resulting from the instantiation of the `ModelDomain` class (A). Sewer network layout requirements: existing building, roads, and collection point (WWTP) (B).\label{fig:fig2}](./media/figures/figure2.png)

## Generating a gravity flow-prioritise sewer network

Within the computational framework of pysewer, the routing and optimisation modules function as the principal mechanisms for synthesising the sewer network. The objective of the routing module is to identify the paths through the network, starting from the sink. The algorithm approximates the directed Steiner tree (the Steiner arborescence) between all sources and the sink by using a repeated shortest path heuristic (RSPH). The routing module has two solvers to find estimates for the underlying minimum Steiner arborescence tree problem; these are:

1. The RSPH solver iteratively connects the nearest unconnected node (regarding distance and pump penalty) to the closest connected network node. The solver can account for multiple sinks and is well-suited to generate decentralised network scenarios.
2. The RSPH Fast solver derives the network by combining all shortest paths to a single sink. It is faster but only allows for a single sink.

In a nutshell, these solvers work by navigating through the connection graph (created using the `generate_connection_graph` method of the preprocessing module). This method simplifies the connection graph, removes any self-loops, sets trench depth node attributes to 0, and calculates the geometry, distance, profile, whether a pump is needed weight, and elevation attributes for each edge and node. The shortest path between the subgraph and terminal nodes in the connection graph is found using Dijkstra’s Shortest Path Algorithm. The RSPH solver repeatedly finds the shortest path between the subgraph nodes and the closest terminal node, adding the path to the sewer graph and updating the subgraph nodes and terminal nodes. Terminal nodes refer to the nodes in the connection graph that need to be connected to the sink. On the other hand, subgraph nodes are the nodes in the directed routed Steiner tree. These are initially set to the sink nodes and are updated as the RSPH solver is applied to find the shortest path between the subgraph and the terminal nodes. This way, all terminal nodes are eventually connected to the sink.

Subsequently, the optimisation module takes the preliminary network generated by the routing module and refines it by assessing and incorporating the hydraulic elements of the sewer network. Here, the hydraulic parameters of the sewer network are calculated. The calculation focuses on the placement of pump or lifting stations on linear sections between road junctions. It considers the following three cases:

1. Terrain does not allow for gravity flow to the downstream node (this check uses the `needs_pump` attribute from the preprocessing to reduce computational load)—placement of a pump station is required.
2. Terrain does not require a pump, but the lowest inflow trench depth is too low for gravitational flow—placement of a lift station is required.

Gravity flow is possible within given constraints—the minimum slope is achieved, no pump or lifting station is required.
As our tool strongly focuses on prioritising gravity flow, a high pump penalty is applied to minimise the length of the pressure sewers. The pumping penalty expressed as the edge weight is relative to the trench depth required to achieve minimum slope to achieve self-cleaning velocities in a gravity sewer. The maximum trench depth $t_{\text{max}}$ required to achieve the minimum slope is set at $t_{\text{max}} = 8$ in the default settings of pysewer. When there is a need to dig deeper than this predefined value, then a pump is required.

The optimisation module also facilitates the selection of the diameters to be used in the network and peak flow estimation, as well as the key sewer attributes such as the number of pump or lifting stations, the length of pressure and gravity sewers, which can be visualised and exported for further analysis. \autoref{fig:fig3} shows an example of a final sewer network layout generated after running the calculation of the hydraulics parameters.

![Pysewer optimisation. Final layout of the sewer network.\label{fig:fig3}](./media/figures/figure3_sewer_network_layout.png)

## Visualising and exporting the generated sewer network

The plotting and exporting module generates visual and geodata outputs. It renders the optimised network design onto a visual map, offering users an intuitive insight into the proposed infrastructure. Sewer network attributes such as the estimated peak flow, the selected pipe diameter (exemplified in \autoref{fig:fig4}) and the trench profile are provided in the final geodataframe. They can be exported as geopackage, shapefile or geoparquet, facilitating further analysis and detailed reporting in other geospatial platforms.

![Pysewer visualisation. Attributes of the sewer network layout. Peak flow estimation (A), Pipe diameters selected (B)\label{fig:fig4}](./media/figures/figure4_peakflow_diameter.png)

# Acknowledgement

M.S. and J.F. were supported by the MULTISOURCE project, which received funding from the European Union’s Horizon 2020 program under grant agreement 101003527. G.K. and D.D. were supported by the WATERUN project, which was funded from the European Union’s Horizon 2020 program under grant agreement 101060922. We thank Ronny Gey from the UFZ Research Data Management (RDM) group for reviewing the git repository.

# Software citations

Pysewer was written Python 3.10.6 and used a suite of open-source software packages that aided the development process:

- Geopandas 0.9.0 [@kelsey_jordahl_2020_3946761]
- Networkx 3.1 [@SciPyProceedings_11]
- Numpy 1.25.2 [@harris2020array]
- Matplotlib 3.7.1 [@Hunter:2007]
- Sklearn 1.0.2 [@scikit-learn]
- GDAL 3.0.2 [@gdal]

# References
