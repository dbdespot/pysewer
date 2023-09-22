try:
    from osgeo import ogr
except ImportError as e:
    raise Exception(""" ERROR: Could not find the GDAL/OGR Python library bindings. 
               On Debian based systems you can install it with this command:
               apt install python-gdal""") from e

#Importing everything allows to use "import pysewer" and then access all functions on the same level e.g. pysewer.ModelDomain()
from pysewer.helper import *
from .optimization import *
from .plotting import *
from .preprocessing import *
from .routing import *

