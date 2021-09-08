Create a GEE asset compatible with SEPAL
========================================

In the current release of SEPAL, Custom assets can be displayed in the main interface to overlay different information in the same place. 
As the main goal of this librairy is to create assets in the the SEPAL framework and as :code:`sepal_ui` is bound to GEE for many modules, we will present you here the different way of creating an :code:`Image` asset that can be automatically displayed in SEPAL and remain consitent with what you display in your app. 

create a visualization 
----------------------

To create an :code:`ee.Image` compatible with the visualization tool of SEPAL, add extra-properties to the :code:`ee.Image` using the :code:`set` method:

.. code-block:: python

    import ee 

    image # an ee.Image created by previous scripts

    ee_image.set({
        "visualization_0_name": "Classification",
        "visualization_0_bands": "red,blue,green",
        "visualization_0_type": "rgb",
        "visualization_0_min": "0",
        "visualization_0_max": "2000"
    })

To create visualization parameter, property have been add as a json dictionnary to the image. 

.. note::

    You can set as many visualization in the dictionnary as you want. Each one will be differentiated by it's ID number and interpreted separately by the SEPAL interface.

Each key of this dictionnary should start with :code:`visualisation_<number>_<keyword>: <value>` with: 

-   :code:`number`: the visualization ID number
-   :code:`keyword`: the keyword to specify the visualization property you want to set 
-   :code:`value`: the value of the property set as a string. if multiple value need to be set (e.g :code:`bands`) they need to be split using comas in the same string.

.. note::

    In the next parts only the keywords will be specified.
    To reproduce our example you can check the following asset: :code:`users/wiell/forum/visualization_example`

.. figure:: ../../img/tutorials/create_asset/all_viz_example.png
   :alt: all viz example
   :align: center

RGB false colors 
----------------
This is setting a 3 bands false color visualization. Each band will be represented as red green and blue (respectively) on the final display. It is compulsory to set at least the **type** key to :code:`rgb`. The other available keys are the following: 

-   **name**: The name that will be displayed in the SEPAL insterface.
-   **bands**: The 3 bands to display. Each one **must** correspond to an existing band in your image. It can be numbers or names. 
-   **gamma**: Set the gamma of the image. It should be a float.
-   **min**: The minimal value to use in all bands or the minimal value to use in each band. Use comas to separate the different values. 
-   **max**: The maximal value to use in all bands or the maximal value to use in each band. Use comas to separate the different values. 
-   **inverted**: Boolean, wether or not the bands should be read inverted. Can also be set individually for each band using comas.

An example of Image property using the example asset: 

.. code-block:: json

    {
        "visualization_0_type": "rgb",
        "visualization_0_name": "RGB",
        "visualization_0_bands": "red,green,blue",
        "visualization_0_gamma": "1.2",
        "visualization_0_min": "0",
        "visualization_0_max": "2000"
    }

and the corresponding display: 

.. figure:: ../../img/tutorials/create_asset/viz_rgb.png
   :alt: rgb display
   :align: center


HSV false colors
---------------- 

This is setting 3 band false color visualization. Each band will be represented as Hue Saturation and Value (respectively) on the final display. It is compulsory to set at least the **type** key to :code:`hsv`. The other available keys are the following: 

-   **name**: The name that will be displayed in the SEPAL insterface.
-   **bands**: The 3 bands to display. each one **must** correspond to an existing band in your image. It can be numbers or names. 
-   **min**: The minimal value to use in all bands or the minimal value to use in each band. Use comas to separate the different values. 
-   **max**: The maximal value to use in all bands or the maximal value to use in each band. Use comas to separate the different values. 
-   **inverted**: Boolean, wether or not the bands should be read inverted. Can also be set individually for eeach band using comas.

An example of Image property using the example asset: 

.. code-block:: json

    {
        "visualization_0_type": "hsv",
        "visualization_0_name": "NDWI harmonics",
        "visualization_0_bands": "ndwi_phase_1,ndwi_amplitude_1,ndwi_rmse",
        "visualization_0_inverted": "false,false,true",
        "visualization_0_min": "-2.1875,352,320",
        "visualization_0_max": "2.40625,3296,1792"
    }

and the corresponding display: 

.. figure:: ../../img/tutorials/create_asset/viz_hsv.png
   :alt: rgb display
   :align: center

Single band continuous
----------------------

This is setting single band ramp color visualization. The band will be represented with the selected colormap on the final display. It is compulsory to set at least the **type** key to :code:`continuous`. The other available keys are the following: 

-   **name**: The name that will be displayed in the SEPAL insterface.
-   **bands**: The band to display. It **must** correspond to an existing band in your image. It can be numbers or names. 
-   **min**: The minimal value to use for the band.
-   **max**: the maximal value to use for the band.
-   **palette**: The colors to use in the ramp. They should be set as hex (e.g. #000000) values separated with comas.

An example of Image property using the example asset: 

.. code-block:: json

    {
        "visualization_0_type": "continuous",
        "visualization_0_name": "NDWI",
        "visualization_0_bands": "ndwi",
        "visualization_0_palette": "#042333,#2c3395,#744992,#b15f82,#eb7958",
        "visualization_0_max": "6610",
        "visualization_0_min": "-8450"
    }

and the corresponding display: 

.. figure:: ../../img/tutorials/create_asset/viz_ramp.png
   :alt: rgb display
   :align: center

Single band categorical
-----------------------

This is setting single band categorical visualization. The band will be represented with the selected colors for each value on the final display. It is compulsory to set at least the **type** key to :code:`categorical`. The other available keys are the following: 

-   **name**: the name that will be displayed in the SEPAL insterface.
-   **bands**: the band to display. It **must** correspond to an existing band in your image. It can be numbers or names. 
-   **palette**: The colors to use in the ramp. They should be set as hex values (e.g. #000000) separated with comas.
-   **labels**: The labels of each category. Use names separated with comas.
-   **values**: the values of each category. Use integer separated with comas.

An example of Image property using the example asset: 

.. code-block:: json

    {
        "visualization_0_type": "categorical",
        "visualization_0_name": "CLASS",
        "visualization_0_bands": "class",
        "visualization_0_palette": "#042333,#b15f82,#e8fa5b",
        "visualization_0_labels": "Foo,Bar,Baz",
        "visualization_0_values": "5,200,1000"
    }

and the corresponding display: 

.. figure:: ../../img/tutorials/create_asset/viz_class.png
   :alt: rgb display
   :align: center
