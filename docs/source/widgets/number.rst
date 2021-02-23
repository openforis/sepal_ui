Number Field
============

:code:`NumberField` is a field widget to enter number with an incremental arrow. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`TextField` ipyvuetify class can be used to complement it.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    number = sw.NumberField()

.. image:: ../../img/number_field.png
    :alt: number

the value can be retreive from the :code:`v_model` trait. 

.. code-block:: python 

    # will return the value of the widget 
    number.v_model 

    # will be thown when v_model change
    number.observe(lambda change: print(change['new'])) 

    # bin the value to a io object using an Alert widget
    sw.Alert().bind(number, io, 'number_attr') 

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.inputs.NumberField>`_.