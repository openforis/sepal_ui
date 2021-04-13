Pasword field
=============

:code:`PasswordField` is a field widget to input passwords in text area and toggle its visibility. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`TextField` ipyvuetify class can be used to complement it.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    password = sw.PasswordField(label = "my password")

.. image:: ../../img/password.png
    :alt: password

the value can be retreive from the :code:`v_model` trait. 

.. code-block:: python 

    # will return the value of the widget 
    password.v_model 

    # will be thown when v_model change (but it will be dangerous to print it ;-) 
    password.observe(lambda change: print(change['new']), 'v_model') 

    # bind the value to a io object using an Alert widget. As it's a password use the secret or non verbose option.
    sw.Alert().bind(password, io, 'password_attr', secret = True)
    sw.Alert().bind(password, io, 'password_attr', verbose =False) 

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.PasswordField>`_.
