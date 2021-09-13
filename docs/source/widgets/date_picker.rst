Date picker
===========

Overview
--------

:code:`DatePicker` is a field widget to enter dates in the "YYY-MM-DD" format. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Layout` ipyvuetify class can be used to complement it.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    date = sw.DatePicker()
    date

.. tip::

    You need to click outside of the slot to validate your selection


the value can be retrieve from the :code:`v_model` trait.

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.DatePicker>`__.
