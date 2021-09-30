AssetSelect
===========

Overview
--------

:code:`AssetSelect` is a field widget to search for asset in the user GEE root folder. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Combobox` ipyvuetify class can be used to complement it.

.. jupyter-execute:: 
    :raises:
    
    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    # to allow the build of the doc in a distanct server
    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    asset_select = sw.AssetSelect(folder=FOLDER)
    asset_select
    
the value can be retrieve from the :code:`v_model` trait. 

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.AssetSelect>`__.