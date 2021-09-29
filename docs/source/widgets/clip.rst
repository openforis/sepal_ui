CopyToClip
==========

Overview
--------

:code:`CopyToClip` is a custom textField that provides a handy copy-to-clipboard javascript behaviour. When the clipboard btn is clicked the :code:`v_model` will be copied in the local browser clipboard. You just have to change the clipboard :code:`v_model`before displaying it to the end user to have a custom value. When copied, the icon change from a copy to a check.
Any argument from the original :code:`TextField` ipyvuetify class can be used to complement it.

.. jupyter-execute:: 
    :raises:

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    clip = sw.CopyToClip(v_model="toto")
    clip

You can also dynamically change the :code:`v_model` value. 

.. note::

    The :code:`TextField` widget is in readonly mode to aoid modifications from the end user.
    
.. jupyter-execute::
    :raises:

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    clip = sw.CopyToClip()
    clip.v_model = "toto"
    clip

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.CopyToClip>`__.