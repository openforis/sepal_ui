TileDisclaimer
==============

Overview
--------

:code:`TileDisclaimer` is a :code:`TileAbout` using a the generic disclaimer .md file. This tile will have the “about_widget” id and “Disclaimer” title. it inherits from the :code:`TileAbout` class.

In the following example we create a fake file on the fly and use it to display somme text in a :code:`AboutTile`. 

.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    from pathlib import Path 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    disclaimer_tile = sw.TileDisclaimer()
    disclaimer_tile

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.tile.TileDisclaimer>`__.