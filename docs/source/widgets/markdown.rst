Markdown
========

:code:`Markdown` is a widget to display `markdown <https://www.markdownguide.org/basic-syntax/>`_ flavored strings. it inherits from the :code:`SepalWidget` class.

.. code-block:: python 

    from sepal_ui import sepalwidgets as sw

    str = """  
        **I am a title**    
        I am some regular text
    """

    mkd = sw.Markdown(str)
    mkd

.. image:: ../../img/markdown.png
    :alt: markdown

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.Markdown>`_.