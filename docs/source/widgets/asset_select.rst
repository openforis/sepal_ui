Asset select
============

:code:`AssetSelect` is a field widget to search for asset in the user GEE root folder. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Combobox` ipyvuetify class can be used to complement it.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    asset_select = sw.AssetSelect()

.. image:: ../../img/asset_select.png
    :alt: asset_select

the value can be retrieve from the :code:`v_model` trait. 

.. code-block:: python 

    # will return the value of the widget 
    asset_select.v_model 

    # will be thown when v_model change
    asset_select.observe(lambda change: print(change['new'])) 

    # bin the value to a io object using an Alert widget
    sw.Alert().bind(asset_select, io, 'asset_attr') 

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.AssetSelect>`__.