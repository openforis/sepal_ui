Download Btn
============

Overview
--------

:code:`DownloadBtn` is custom widget to provide easy to use button in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Btn` ipyvuetify class can be used to complement it. It is used to store download path.
The default color is set to "success". if no URL is set the button is disabled.

.. jupyter-execute:: 

    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    btn = sw.DownloadBtn(text = "a file")
    btn
    
Methods
-------

the linked URL can be dynamically set with the :code:`set_url` method.

.. jupyter-execute:: 

    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    btn = sw.DownloadBtn(text = "Pokepedia")
    btn.set_url('https://www.pokepedia.fr/images/7/76/Pikachu-DEPS.png')
    btn

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.btn.DownloadBtn>`__.