App
===

Overview
--------

:code:`App` is a custom :code:`App` display with the tiles created by the user using the sepal color framework. 
Display false :code:`AppBar` if not filled. 
:code:`NavDrawer` is fully optional. 
The :code:`drawerItem` will be linked to the app tile and they will be able to control their display If the :code:`NavDrawer` exists, it will be linked to the :code:`Appbar` :code:`togglebtn`.

.. danger::

    This component should never be launched from the kernel but only in voila dashboard. The Javascript components would overlay on top of the Notebook window.

.. jupyter-execute:: 
    :raises:

    from sepal_ui import sepalwidgets as sw
    from sepal_ui import aoi
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    app = sw.App(
        tiles    = [sw.TileDisclaimer(), aoi.AoiTile(gee=False)], 
        appBar   = sw.AppBar(), 
        footer   = sw.Footer(), 
        navDrawer= sw.NavDrawer([
            sw.DrawerItem('aoi', card='aoi_widget'),
            sw.DrawerItem('disc', card='about_widget')
        ])
    ).show_tile('aoi_widget') # id of the tile you want to display

    # Uncomment this line in a voila executed notebook 
    #app

.. figure:: ../../img/widget/app.png
    :alt: app


.. note::

    The :code:`App` component is the main widget of the framework. To learn how to use it, read our cookbook.  
    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.app>`__.