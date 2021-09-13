About tile
==========

:code:`TileAbout` is a widget to display `markdown <https://www.markdownguide.org/basic-syntax/>`_ flavored file to describe the module. it inherits from the :code:`Tile` class.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    from pathlib import Path 

    tmp_file = Path('~', 'tmp', 'tmp_mkd.md').expanduser()

    with tmp_file.open('w') as f:
        f.write('## It is a first section  \n')
        f.write(' Lorem ipsum')
    
    about_tile = sw.TileAbout(tmp_file)
    about_tile

.. tip:: 

    The file should be starting with a level 2 header as the title of the tile ("About") is already using the level 1

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.tile.TileAbout>`__.