StateBar
========

Overview
--------

:code:`Statebar` is a custom widget to provide easy to use state bars in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
any argument from the original :code:`SystemBar` ipyvuetify class can be used to complement it.

.. jupyter-execute::
    :raises:
    :stderr:
    
    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    statebar = sw.StateBar()
    statebar

Methods
-------

State bar can be stopped using the following code. The :code:`msg` can be changed according to your need. 

.. tip::
    
    You can also change the message without stopping the loading by omitting the second parameter
    
.. jupyter-execute::
    :raises:
    :stderr:
    
    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    statebar = sw.StateBar()
    statebar.add_msg('ongoing', True)

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.alert.StateBar>`__.