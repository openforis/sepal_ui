"""Package to gather all the tiles created in the application.

If you only have few widgets, a module is not necessary and you can simply use a tile.py file
In a big module with lot of custom tiles, it can make sense to split things in separate files for the sake of maintenance
If you use a module import all the functions here to only have 1 call to make.
"""

from .map_tile import *
