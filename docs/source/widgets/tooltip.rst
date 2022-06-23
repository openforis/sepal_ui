Tooltip
=======

In sepal-ui we have two ways to set tooltips to the widgets. The first one is the built-in :code:`sepalwidget.set_tooltip()` method available for all widgets, and the external one called :code:`sw.Tooltip(*args)`, depending on your needs you'll be probably more in favor in one than the other.


Built-in
--------
Built-in tooltip is a new feature supported by :code:`sepal_ui>=2.9.0`. This integration makes possible to easily wrap a widget with a tooltip. Due to all sepal widgets are inheriting from the base :code:`sepal_ui.sepalwidget` class, it is possible to call the :code:`set_tooltip()` method from any component.

Calling this method will store the tooltip view as a parameter of the widget (called :code:`with_tooltip`), it means that if you want to display the tooltip you'll have to use this element i.e. :code:`widget.with_tooltip`. As the widget now is activated and handled by the tooltip, it won't be longer displayed by itself (i.e. :code:`widget` will be invisible).

Remember that, even though the widget is wrapped by the tooltip, the widget methods and events have to be called from the element itself.

.. jupyter-execute::
    :raises:
    
    from sepal_ui import sepalwidgets as sw 

    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v 
    v.theme.dark = False

    btn = sw.Btn('click')
    btn.set_tooltip("Built-in tooltip", bottom=True)

    # Note that calling btn won't display anything
    btn
    
    # Create events
    btn.on_event("click", lambda *_: print("test"))
    
    # And to display it..
    btn.with_tooltip

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.SepalWidget.set_tooltip>`__.

External
--------

The external :code:`Tooltip` is a custom widget to provide easy to use tooltip in the sepal_ui framework. We are based on the Vuetify web structure so the design of the tooltip design can be surprising for users coming from different platform. Here the tooltip is the main widget, and it owns the widget it describes. Here is an example for a :code:`Btn`.

.. jupyter-execute::
    :raises:
    
    from sepal_ui import sepalwidgets as sw 
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v 
    v.theme.dark = False

    btn = sw.Btn('click')
    sw.Tooltip(widget=btn, tooltip='Click over the button')

.. note::

    More information can be found `here <../modules/sepal_ui.sepalwidgets.html#sepal_ui.sepalwidgets.sepalwidget.Tooltip>`__.