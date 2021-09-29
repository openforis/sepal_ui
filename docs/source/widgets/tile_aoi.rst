AoiTile
=======

Overview
--------

:code:`AoiTile` is a :code:`Tile` tailored for the selection of an AOI. 
Render and bind all the variable to create an autonomous AOI selector. 
If you use a custom AOI, it will create a asset in you gee account with the name :code:`aoi_[aoi_name]`.
It inherits from the :code:`SepalWidget` class. Any argument from the original :code:`Card` ipyvuetify class can be used to complement it. You can choose either or not you want to use the gee binding.

.. jupyter-execute::
    :raises:

    from sepal_ui import aoi 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    aoi_tile = aoi.AoiTile(gee=False)
    aoi_tile

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.tile.Tile>`__.
