Btn
===

Overview
--------

:code:`Btn` is custom widget to provide easy to use button in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Btn` ipyvuetify class can be used to complement it. The button icon needs to be searched in the `fontAwesome library <https://fontawesome.com/v5.15/icons>`__ or mdi library <https://materialdesignicons.com>`_, if none is set, a :code:`fas fa-check` will be used.
The default color is set to "primary".  

.. jupyter-execute:: 
    :raises:
    :stderr:

    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    btn = sw.Btn(
        text = "The One btn",
        icon = "fas fa-cogs"
    )
    btn
    
Methods
-------

Btn can be used to launch function on any Javascript event such as "click".

.. jupyter-execute::
    :raises:
    :stderr:

    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    btn = sw.Btn(
        text = "The One btn",
        icon = "fas fa-cogs"
    )
    btn.on_event('click', lambda *args: print('Hello world!'))
    
    btn

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.btn.Btn>`__.