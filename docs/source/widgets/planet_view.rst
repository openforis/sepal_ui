PlanetView
==========

Planet view is a stand-alone interface able to capture credentials and log-in to planet API service. The user has the option to select between two log-in methods, through an API key or credentials (username + password) and managing exceptions. 

This component is linked with its planet model and can be accessed as a parameter. Please refer to `planet_model <../modules/sepal_ui.modules.html#sepal_ui.planetapi.PlanetModel>`__ to more detailed info.

.. jupyter-execute:: 
    :raises:

    from sepal_ui.planetapi import PlanetView
    
    # correct colors for the documentation 
    # set to dark in SEPAL by default 
    import ipyvuetify as v
    v.theme.dark = False

    planet_view = PlanetView()
    v.Card(max_width=600, children=[planet_view])

.. note::

    More information can be found `here <../modules/sepal_ui.modules.html#sepal_ui.planetapi.PlanetView>`__.
