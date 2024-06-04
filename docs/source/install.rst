.. SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
.. SPDX-License-Identifier: GPL-3.0-only

Installation 
============

Currently the installation is easiest managed via Anaconda. Anaconda 3 can be downloaded [here.](https://www.anaconda.com/products/individual).
The package is tested with **Python 3.10.6**. We recommend using a conda environment to manage the installation of GDAL and other dependencies given the difficulty of installing GDAL using pip.
Therefore we urge to first create a new conda environment and install the required packages.  

**Please use conda to install GDAL, it is the easiest way to install GDAL**

Step 1 Clone the repository and navigate to the root directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    git clone https://github.com/dbdespot/pysewer.git
    cd pysewer


Step 2: Create the conda environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here you create a conda environment (pysewer) and install the required packages.  We recommend directly installing GDAL, Rasterio and Fiona using conda.

Creating the conda environment:
.. code::

    conda create -n pysewer python=3.10.6


Activate the environment:
.. code::

    conda activate pysewer

Install the required packages:
.. code::

    conda install -c conda-forge gdal

All other packages are installed via pip during the installation of pysewer.
Note that the exact versions of the packages used can be found in the [environment.yml](environment.yml) file. 

Step 3: Install pysewer via pip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that you have conda environment uo and running, lets install pysewer. To do this you first need to clone pysewer repository hosted [here.](https://github.com/dbdespot/pysewer) and install it using git and pip with:

.. code-block:: bash

    cd pysewer
    pip install .
    # for the development version
    python -m pip install -e .


