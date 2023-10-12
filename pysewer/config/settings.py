"""
SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
SPDX-License-Identifier: GNU GPLv3

"""
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Union

import geopandas as gpd
import networkx as nx
import pandas as pd
import yaml

# get the directory of the current file
current_directory = Path(os.path.dirname(os.path.realpath(__file__)))

DEFAULT_SETTINGS_PATH = str(current_directory / "settings.yaml")


@dataclass
class Preporocessing:
    dem_file_path: Optional[str]
    roads_input_data: Optional[Union[str, gpd.GeoDataFrame]]
    buildings_input_data: Optional[Union[str, gpd.GeoDataFrame]]
    dx: int
    pump_penalty: int
    max_connection_length: int
    clustering: str
    connect_buildings: bool
    add_private_sewer: bool
    field_get_sinks: str
    field_get_buildings: str
    value_get_sinks: str
    value_get_buildings: str


@dataclass
class Optimization:
    inhabitants_dwelling: int
    daily_wastewater_person: float
    peak_factor: float
    min_slope: float
    tmax: float
    tmin: float
    inflow_trench_depth: float
    min_trench_depth: float
    diameters: List[float]
    roughness: float
    pressurized_diameter: float


@dataclass
class Plotting:
    plot_connection_graph: bool
    plot_junction_graph: bool
    plot_sink: bool
    plot_sewer: bool
    hillshade: bool
    colormap: str
    sewer_graph: nx.Graph = None
    info_table: Optional[dict] = None


@dataclass
class Export:
    file_format: str


@dataclass
class Config:
    preprocessing: Preporocessing
    optimization: Optimization
    plotting: Plotting
    export: Export


def load_settings(file_path: Optional[str] = None):
    with open(file_path, "r") as file:
        settings = yaml.safe_load(file)
    return settings


def deep_merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination


def override_settings(
    custom_path: Optional[str] = None, custom_setting_dict: Optional[dict] = None
):
    """
    Override the settings with a custom settings file or a custom dictionary.
    """

    settings = load_settings(file_path=DEFAULT_SETTINGS_PATH)

    if custom_path:
        custom_settings = load_settings(file_path=custom_path)
        settings = deep_merge(custom_settings, settings)
    elif custom_setting_dict:
        settings.update(custom_setting_dict)
        deep_merge(custom_setting_dict, settings)
    else:
        raise ValueError(
            "Either custom_path or custom_setting_dict should be provided."
        )
    return settings


def override_setting_to_config(
    custom_path: str = None, custom_setting_dict: dict = None
):
    # load the settings as dictionary
    settings_dict = override_settings(
        custom_path=custom_path, custom_setting_dict=custom_setting_dict
    )

    # convert the dictionary to a Config object
    processing_config = Preporocessing(**settings_dict["preprocessing"])
    optimization_config = Optimization(**settings_dict["optimization"])
    plotting_config = Plotting(**settings_dict["plotting"])
    export_config = Export(**settings_dict["export"])

    return Config(
        preprocessing=processing_config,
        optimization=optimization_config,
        plotting=plotting_config,
        export=export_config,
    )


def load_config(custom_path: str = None, custom_setting_dict: dict = None) -> Config:
    """
    Load the default settings and override them with custom settings if needed.
    """

    default_settings = override_setting_to_config(DEFAULT_SETTINGS_PATH)

    # if default settings if of class .Conifg
    if isinstance(default_settings, Config):
        # print("default_settings is of class Config")
        if custom_path:
            custom_settings = override_setting_to_config(custom_path)
            default_settings.preprocessing = custom_settings.preprocessing
            default_settings.optimization = custom_settings.optimization
            default_settings.plotting = custom_settings.plotting
            default_settings.export = custom_settings.export
        elif custom_setting_dict:
            default_settings.preprocessing = custom_setting_dict["preprocessing"]
            default_settings.optimization = custom_setting_dict["optimization"]
            default_settings.plotting = custom_setting_dict["plotting"]
            default_settings.export = custom_setting_dict["export"]
    else:
        raise ValueError(
            "Either custom_path or custom_setting_dict should be provided."
        )
    return default_settings


def flatten_config(config_dict, parent_key="", sep="_"):
    items = {}
    for k, v in config_dict.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_config(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def config_to_dataframe(config: Config) -> pd.DataFrame:
    config_dict = asdict(config)
    flat_config = flatten_config(config_dict)
    df = pd.DataFrame(list(flat_config.items()), columns=["Setting", "Value"])
    return df

# view defaults settings
def view_default_settings():
    default_settings = override_setting_to_config(DEFAULT_SETTINGS_PATH)
    df = config_to_dataframe(default_settings)
    return df

# if __name__ == "__main__":
#     # test the deault settings using config class

#     Config1 = load_config()
#     print(Config1)
#     print(type(Config1))

#     # assessing values
#     print(Config1.preprocessing.dx)

#     print("Done!!")
