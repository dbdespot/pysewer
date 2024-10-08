# SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
# SPDX-License-Identifier: GPL-3.0-only

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pysewer",
    version="0.1.17",
    description="A Python Package for automated routing and optimization of sewer networks",
    license="GNU GPLv3",
    packages=find_packages(),
    package_data={
        'pysewer.config': ['*.yaml'],  # Include all YAML files in the pysewer/config directory
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU GPLv3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "rasterio",
        "matplotlib",
        "pyyaml",
        "pandas",
        "geopandas",
        "pyproj",
        "shapely",
        "fiona>=1.9.2",
        "ipython",
        "ipykernel",
        "scipy",
        "scikit-learn",
        "networkx",
        "pyarrow",
        "earthpy",
        "pytest",
        "jupyterlab",
    ],
    python_requires=">=3.10",
)
