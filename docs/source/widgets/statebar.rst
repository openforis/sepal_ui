Statebar
========

:code:`Statebar` is a custom widget to provide easy to use state bars in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
any argument from the original :code:`Btn` ipyvuetify class can be used to complement it.

.. code-block:: python

    from sepal_ui import sepalwidgets as sw 

    statebar = sw.StateBar()
    
.. image:: ../../img/statebar.png

State bar can bbe stopped using the following code. The :code:`msg`can be changed according to your need. 

.. tip::
    
    You can also change the message without stoping the loading by ommiting the second parameter
    
.. code-block:: python 

    statebar.add_msg('finished', True)
    
.. image:: ../../img/statebar_finished.png

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.alert.StateBar>`_.