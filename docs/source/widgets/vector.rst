VectorField
===========

Overview
--------

:code:`VectorField` is a field widget to load points data. 
A custom input widget to load vector data. The user will provide a vector file compatible with fiona.
The user can then select a specific shape by setting column and value fields.
It inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Layout` ipyvuetify class can be used to complement it.

.. jupyter-execute:: 
    :raises:
    :stderr:

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    vectr_field = sw.VectorField()
    vectr_field

the value can be retrieve from the :code:`v_model` trait.

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.VectorField>`_.