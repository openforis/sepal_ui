About tile
==========

Overview
--------

:code:`TileAbout` is a widget to display `markdown <https://www.markdownguide.org/basic-syntax/>`_ flavored file to describe the module. it inherits from the :code:`Tile` class. To use it create a file containing some mkd content and use it as a first argument of the tile. The content will be display as in GitHub.

In the following example we create a fake file on the fly and use it to display somme text in a :code:`AboutTile`. 

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    from pathlib import Path 
    import ipyvuetify as v
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False
    
    # create the widget
    tmp_file = Path.home()/'tmp'/'tmp_mkd.md'
    
    tmp_file.write_text('## It is a first section  \n')
    tmp_file.write_text(' Lorem ipsum')
    
    about_tile = sw.TileAbout(tmp_file)
    about_tile
    
.. tip:: 

    The file should be starting with a level 2 header (`-`) as the title of the tile ("About") is already using the level 1.

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.tile.TileAbout>`_.