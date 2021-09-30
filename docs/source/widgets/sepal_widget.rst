SepalWidget
===========

Overview
--------

:code:`SepalWidget` is an abstract object that embed special classes, it can be used with any ipyvuetify widget component:

.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    class SepalSelect(sw.SepalWidget, v.Select):

        def __init__(self, **kwargs):

            super().__init__(**kwargs)
            
    sepal_select = SepalSelect()
    sepal_select
    
Methods
-------

This abstract class add 3 method to the ipyvuetify objects

hide
^^^^

Hide the component by changing its class.

.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    class SepalSelect(sw.SepalWidget, v.Select):

        def __init__(self, **kwargs):

            super().__init__(**kwargs)
            
    sepal_select = SepalSelect()
    sepal_select.hide()

show
^^^^

Show the component by changing its class.

.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    class SepalSelect(sw.SepalWidget, v.Select):

        def __init__(self, **kwargs):

            super().__init__(**kwargs)
            
    sepal_select = SepalSelect()
    sepal_select.hide().show()

reset
^^^^^

remove the :code:`v_model` of the component and replace it by :code:`None`.

.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    v.theme.dark = False

    class SepalTextField(sw.SepalWidget, v.TextField):

        def __init__(self, **kwargs):

            super().__init__(**kwargs)
            
    sepal_select = SepalTextField(v_model='toto')
    print(sepal_select.v_model)
    sepal_select.reset()

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.SepalWidget>`__.