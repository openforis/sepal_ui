Sepal widget
============

:code:`SepalWidget` is an abstract object that embed special classes, it can be used with any ipyvuetify widget component:

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw
    import ipyvuetify as v 

    class SepalSelect(sw.SepalWidget, v.Select):

        def __init__(self, **kwargs):

            super().__init__(**kwargs)

.. code-block:: python 

    sepal_select = SepalSelect()
    sepal_select

.. image:: ../../img/sepalselect.png
    :alt: sepalselect

The component can now be hidden with :code:`hide` and :code:`show` methods.

.. code-block:: python 

    sepal_select.hide() 

.. code-block:: python

    sepal_select.show()

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.SepalWidget>`_.