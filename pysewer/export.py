"""
Since the profile and trench_depth_profile are list of tuples, they cannot be exported 
to a shapefile or GeoPackage directly using the native GeoPandas function (to_file). 
This module contains functions to convert the list of tuples to JSON strings, 
which can then be exported to a shapefile or GeoPackage. 
The option saving the data as a parquet file is added.

"""

import json
from typing import List, Tuple

import fiona
import geopandas as gpd


def is_list_of_tuples(lst: List) -> bool:
    """
    Check if a list contains only tuples.

    Parameters
    ----------
    lst : list
        List to check.

    Returns
    -------
    bool
        True if the list contains only tuples, False otherwise.
    """
    return all(isinstance(item, tuple) for item in lst)


def tuple_list_to_json(lst: List[Tuple]) -> str:
    """
    Convert a list of tuples to a JSON string.

    Parameters
    ----------
    lst : list of tuples
        List of tuples to convert.

    Returns
    -------
    str
        JSON string representation of the list of tuples.
    """
    return json.dumps([list(item) for item in lst])


def write_gdf_to_gpkg(gdf: gpd.GeoDataFrame, filepath: str):
    """
    Write a GeoDataFrame to a GeoPackage (GPKG) file using Fiona, converting lists of tuples to JSON strings.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame to write to file.
    filepath : str
        Path to the output file.

    Returns
    -------
    None
    """
    # Convert only columns with list of tuples to JSON strings
    for col in gdf.columns:
        if gdf[col].dtype == "object":
            if is_list_of_tuples(gdf[col]):
                gdf[col] = gdf[col].apply(tuple_list_to_json)

    # Define the schema based on the GeoDataFrame
    schema = {
        "geometry": gdf.geometry.type.iloc[0],
        "properties": {
            col: "str" if is_list_of_tuples(gdf[col]) else gdf[col].dtype.name
            for col in gdf.columns
            if col != "geometry"
        },
    }

    # Open a new GPKG file in write mode
    with fiona.open(filepath, mode="w", driver="GPKG", schema=schema) as dst:
        for _, row in gdf.iterrows():
            feature = {
                "geometry": row["geometry"].__geo_interface__,
                "properties": {
                    col: row[col] for col in gdf.columns if col != "geometry"
                },
            }
            dst.write(feature)


def write_gdf_to_shp(gdf: gpd.GeoDataFrame, filepath: str) -> None:
    """
    Write a GeoDataFrame to a shapefile using Fiona, converting lists of tuples to JSON strings.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to be written to a shapefile.
    filepath : str
        The file path to write the shapefile to.

    Returns
    -------
    None

    Notes
    -----
    This function converts any columns in the GeoDataFrame that contain lists of tuples to JSON strings before writing
    the GeoDataFrame to a shapefile. The schema of the shapefile is defined based on the GeoDataFrame, with the geometry
    column being defined as the geometry type of the first row of the GeoDataFrame, and all other columns being defined
    as either 'str' or the dtype of the column, depending on whether the column contains lists of tuples or not.
    """
    # Convert only columns with list of tuples to JSON strings
    for col in gdf.columns:
        if gdf[col].dtype == "object":
            if is_list_of_tuples(gdf[col]):
                gdf[col] = gdf[col].apply(tuple_list_to_json)

    # Define the schema based on the GeoDataFrame
    schema = {
        "geometry": gdf.geometry.type.iloc[0],
        "properties": {
            col: "str" if is_list_of_tuples(gdf[col]) else gdf[col].dtype.name
            for col in gdf.columns
            if col != "geometry"
        },
    }

    # Open a new shapefile in write mode
    with fiona.open(filepath, mode="w", driver="ESRI Shapefile", schema=schema) as dst:
        for _, row in gdf.iterrows():
            feature = {
                "geometry": row["geometry"].__geo_interface__,
                "properties": {
                    col: row[col] for col in gdf.columns if col != "geometry"
                },
            }
            dst.write(feature)


import geopandas as gpd


def export_sewer_network(gdf: gpd.GeoDataFrame, filepath: str, file_format: str):
    """
    Export a sewer network GeoDataFrame to a file.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        A GeoDataFrame containing the sewer network.
    filepath : str
        The path to the file to which the sewer network should be exported.
    file_format : str
        The file format to which the sewer network should be exported.
        Currently supported formats are 'gpkg' (GeoPackage) and 'shp' (ESRI Shapefile).

    Raises
    ------
    ValueError
        If the file format is not supported.

    Returns
    -------
    None
    """
    supported_formats = ["gpkg", "shp", "parquet"]
    if file_format not in supported_formats:
        raise ValueError(f"File format {file_format} is not supported.")

    if file_format == "gpkg":
        write_gdf_to_gpkg(gdf, filepath)
    elif file_format == "shp":
        write_gdf_to_shp(gdf, filepath)
    elif file_format == "parquet":
        gdf.to_parquet(
            filepath, index=False
        )  # index set false to avoid AttributeError: module 'pandas' has no attribute 'Int64Index'
    print(f"Successfully exported sewer network to {filepath}.")
