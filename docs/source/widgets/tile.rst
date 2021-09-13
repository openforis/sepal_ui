Tile
====

Overview 
--------

:code:`Tile` is a widget Layout. It's the core element of any sepal_ui app. It inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Card` ipyvuetify class can be used to complement it.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()],
        output = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    tile

.. tip:: 

    The best way to use the tiles in an sepal_ui framework is to use :code:`Tile` as an abstract tile and build specific Tiles adapted to your need in the :code:`component/tile` package. 
    Everything is shown following this `tutorial <../tutorials/add-tile.html>`_.
    
Methods
-------

nest
^^^^

Prepare the tile to be used as a nested component in a tile. The elevation will be set to 0 and the title remove from children. The mount_id will also be changed to "nested".

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()],
        alert = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    
    tile.nest()
    
set_content
^^^^^^^^^^^

Replace the current content of the tile with the provided inputs. it will keep the output and btn widget if existing.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()],
        alert = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    
    tile.set_content([sw.PasswordField()])

set_title
^^^^^^^^^

Replace the current title and activate it. If no title is provided, the title is removed from the tile content.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()],
        alert = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    
    tile.set_title("A custom title")

get_title
^^^^^^^^^

Return the current title of the tile

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()],
        alert = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    
    tile.get_title()
    
toggle_inputs
^^^^^^^^^^^^^

Display only the widgets that are part of the input_list. the widget_list is the list of all the widgets of the tile.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False
    
    inputs = [sw.Markdown('lorem ipsum'), v.Select(), v.TextField()]

    tile = sw.Tile(
        id_ = "tile",
        title = "My first tile",
        inputs = inputs,
        alert = sw.Alert().add_msg('lorem agin ipsum'),
        btn = sw.Btn()
    ) 
    
    tile.toggle_inputs([inputs[2]], inputs)

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.tile.Tile>`_.