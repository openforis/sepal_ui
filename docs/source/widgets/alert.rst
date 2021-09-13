Alert
=====

Overview
--------

:code:`Alert` is a a custom Alert widget. 
It is used as the output of all processes in the framework. 
In the voila interfaces, print statement will not be displayed. Instead use the :code:`sw.Alert` method to provide information to the user. 
It’s hidden by default and the visibility change every time you create a message. 
It inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Alert` ipyvuetify class can be used to complement it.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert().show()
    output
    
Methods
-------

:code:`Alert`object embed several methods that will be displayed in this section.

.. note::

    More information on the methods and their options can be found in the full documentation `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.alert.Alert>`_ 


update_progress
^^^^^^^^^^^^^^^

Update the Alert message with a progress bar

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
add_msg
^^^^^^^

Add a message in the alert by replacing all the existing one.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
    msg1 = 'lorem'
    
    output.add_msg(msg1)
    
add_live_msg
^^^^^^^^^^^^

Add a message in the alert by replacing all the existing one and add a timestamp.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
    msg1 = 'lorem'
    
    output.add_live_msg(msg1)
    
append_msg
^^^^^^^^^^

Append a message in a new parragraph, with or without :code:`Divider`.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
    msg1 = 'lorem'
    msg2 = 'ipsum'
    
    output.add_msg(msg1)
    output.append_msg(msg2)
    
remove_last_msg
^^^^^^^^^^^^^^^

Remove the last msg printed in the Alert widget.

.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
    msg1 = 'lorem'
    msg2 = 'ipsum'
    
    output.add_msg(msg1)
    output.append_msg(msg2)
    output.remove_last_msg()
    
check_input
^^^^^^^^^^^

Check if the inpupt value is initialized.
If not return :code:`False` and display an error message else return :code:`True`.


.. jupyter-execute::

    from sepal_ui import sepalwidgets as sw
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False
    
    output = sw.Alert()
    
    input = None
    
    output.check_input(input)

<<<<<<< HEAD
.. note::
    The Alert component is a key component of the tile component as it can test variable initialization, bind variable to widget, and display processes in voila dashboard. 
    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.alert.Alert>`__.
=======
>>>>>>> 1e06332158e609c67ea699c42646442fe522d4df
