Markdown
========

Basic Example
-------------

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

.. warning::

    - No tabulation must be applyed in the multiline :code:`str`.
    - Don't forget to escape the "`" character, it will be interpreted as code mark

Include multiline mkd in the translation tool 
---------------------------------------------

If you want to use the translation tool AND create multiline mkd text you should consider the following method 

in :code:`en.json` use a list in your key with each element of the list corresponding to a line:

.. code-block:: json
    # component/message/en.json

    {
        #[...]
        "multiline_key": [
            "this is",
            " a multiline",
            "key"
        ]
    }

Then In your notebook you can call the key in a markdown widget and display it as multiline text:

.. code-block:: python 

    from component.message import cm
    from sepal_ui import sepalwidgets as sw 

    mkd = sw.Markdown('  \n'.join(cm.multiline_key))
    mkd

.. tip::

    line break in markdown need to be set with to blank space, if not they will not be interpreted

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.Markdown>`_.