ReclassifyTile
==============

Overview
--------

:code:`ReclassifyTile` is a :code:`Tile` tailored for the creation and usage of a custom classification. Fully autonomous this tile will help you create classification that fit your application and apply it on your inputs.
It inherits from the :code:`SepalWidget` class. Any argument from the original :code:`Card` ipyvuetify class can be used to complement it. You can choose either or not you want to use the gee binding.

.. jupyter-execute::

    from sepal_ui import reclassify as rec
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    reclassify_tile = rec.ReclassifyTile(gee=False)
    reclassify_tile

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.reclassify.reclassify_tile.ReclassifyTile>`_.