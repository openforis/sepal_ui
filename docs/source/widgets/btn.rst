Btn
===

:code:`Btn` is custom widget to provide easy to use btn in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
any argument from the original :code:`Btn` ipyvuetify class can be used to complement it. The btn icon need to be searched in the `mdi librairy <https://materialdesignicons.com>`_, if none is set, a :code:`mdi-check` will be used.
The default color is set to "primary".  

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    btn = sw.Btn(
        text = "The One btn",
        icon = "mdi-cogs"
    )
    btn

.. image:: ../../img/btn.png
    :alt: btn

Btn can be used to launch function on any javascript event such as "click".

.. code-block:: python 

    btn.on_event('click', lambda widget, event, data: print('Hello world!'))

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.btn.Btn>`_.