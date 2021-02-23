App
===

:code:`App`is a custom App display with the tiles created by the user using the sepal color framework. 
Display false appBar if not filled. 
Navdrawer is fully optionnal. 
The drawerItem will be linked to the app tile and they will be able to control their display If the navdrawer exist, it will be linked to the appbar togglebtn.

.. danger::

    This component should never be launched from the kernel but only in voila dashboard. The javascript compoent would overlay on top of the notebook window.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw
    from sepal_ui import aoi

    app = sw.App(
        tiles    = [sw.TileDisclaimer(), aoi.TileAoi(aoi.Aoi_io())], 
        appBar   = sw.AppBar(), 
        footer   = sw.Footer(), 
        navDrawer= sw.NavDrawer([
            sw.DrawerItem('aoi', card='aoi_widget'),
            sw.DrawerItem('disc', card='about_widget')
        ])
    ).show_tile('aoi_widget') # id of the tile you want to display

    app

.. tip::

    If you start your voila dashboard from Jupyter Notebook, add :code:`?voila-theme=dark` at the end of your url.

.. image:: ../../img/app.png
    :alt: app


.. note::
    The :code:`App` component is the main widget of the framework. To learn how to use it, read our cookbook.  
    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.app>`_.