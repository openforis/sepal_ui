NumberField
===========

Overview
--------

:code:`NumberField` is a field widget to enter number with an incremental arrow. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`TextField` ipyvuetify class can be used to complement it.

.. jupyter-execute::
    :raises:
    :stderr:

    from sepal_ui import sepalwidgets as sw

    # correct colors for the documentation
    # set to dark in SEPAL by default
    import ipyvuetify as v
    v.theme.dark = False

    number = sw.NumberField()
    number

the value can be retrieve from the :code:`v_model` trait.

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.NumberField>`__.
