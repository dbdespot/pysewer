from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pysewer",
    version="0.1.13",
    description="A Python Package for automated routing and optimization of sewer networks",
    license="GNU GPLv3",
    packages=["pysewer"],  # same as name
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
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
        "gdal",
    ],
    python_requires=">=3.10",
)
