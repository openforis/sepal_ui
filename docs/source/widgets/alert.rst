Alert
=====

:code:`Alert` is a a custom Alert widget. 
It is used as the output of all processes in the framework. 
In the voila interfaces, print statement will not be displayed. 
Instead use the :code:`sw.Alert` method to provide information to the user. 
It’s hidden by default. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Alert` ipyvuetify class can be used to complement it.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    output = sw.Alert().show()
    output

.. image:: ../../img/alert.png
    :alt: alert

To display messages in the component 3 methods are available :

.. code-block:: python 

    msg1 = 'lorem'
    msg2 = 'ipsum'

    # add one message with a timestamp
    output.add_live_msg(msg1)

    # add a single message by replacing the existing one 
    output.add_msg(msg2)

    # add a message after the existing one 
    output.append_msg(msg1)


.. note::
    The Alert component is a key component of the tile component as it can test variable initialization, bind variable to widget, and display processes in voila dashboard. 
    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.alert.Alert>`_.