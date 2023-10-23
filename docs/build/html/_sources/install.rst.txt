# SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
# SPDX-License-Identifier: GPL-3.0-only

Installation 
============

Currently the installation is easiest managed via Anaconda. Anaconda 3 can be downloaded `here <https://www.anaconda.com/products/individual>`_

Create a new environment
^^^^^^^^^^^^^^^^^^^^^^^^^

First, we want to create a new environment in Anaconda. Therefore, we open Anaconda prompt and create a new Python 3.10 Environment and name it pysewer by running the following command:

.. code::

    conda create -n pysewer python=3.10

We can then activate the environment by running:

.. code::

    conda activate pysewer


For installing GDAL, rasterio and fiona :

.. code::

    conda install -c conda-forge gdal rasterio fiona



Install pysewer via pip
^^^^^^^^^^^^^^^^^^^^^^^^^

You can either get pysewer and install it using git and pip with:

.. code-block:: bash

    git clone https://git.ufz.de/despot/pysewer_dev.git
    cd pysewer
    pip install .
    # for the development version
    python -m pip install -e .
