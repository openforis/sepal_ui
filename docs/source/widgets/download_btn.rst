Download Btn
============

:code:`DownloadBtn` is custom widget to provide easy to use button in the sepal_ui framework. it inherits from the :code:`SepalWidget` class.
Any argument from the original :code:`Btn` ipyvuetify class can be used to complement it. It is used to store download path.
The default color is set to "success". if no URL is set the button is disabled.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    btn = sw.DownloadBtn(text = "a file")
    btn

.. image:: ../../img/download_btn.png
    :alt: btn

the linked URL can be dynamically set with the :code:`set_url` method.

.. code-block:: python 

    btn.set_url('a/relative/url.tif')

.. image:: ../../img/download_btn_enable.png
    :alt: btn enable

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.btn.DownloadBtn>`_.