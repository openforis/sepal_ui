File input
==========

Overview
--------

:code:`FileInput` is a field widget to search for files in the SEPAL folders. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Layout` ipyvuetify class can be used to complement it.

.. jupyter-execute:: 

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    file_input = sw.FileInput()
    file_input

the value can be retrieve from the :code:`v_model` trait.

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.FileInput>`_.