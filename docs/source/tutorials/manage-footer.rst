Manage the app footer
=====================

Edit the footer 
---------------
In the default application, the footer is displaying the fooloowing message : 

.. code-block:: 

    The sky is the limit (c) 2020

This not very useful. If you want to add your name or company name to the footer it's very simple. 
go to the english dictionnary file : 

.. code-block:: python

    # component/message/en.json

    {
        "not_translated": "this message only exist in the en dict",
        "app": {
            "title": "My first module",
            "footer": "The sky is the limit \u00a9 {}",
            "drawer_item": {
                "aoi": "AOI selection",
                "default_process": "Process",
                "default_result": "Results",
                "about": "About"
            }
        },
        "default_process": {
            "small_slider": "{} is not big enought, please provide a value > to 50",
            "end_computation": "Computation complete",
            "hist_title": "Histogram",
            "treecover2000": "Treecover 2000",
            "healthy_veg": "Healthy vegetation",
            "green": "Green",
            "green_update": "Green updated",
            "gain_loss": "Gain & Loss",
            "slider": "Select percentage",
            "textfield": "Write text",
            "title": "Process tile",
            "no_aoi": "Please provide an AOI",
            "no_slider": "Please provide a percentage value",
            "no_textfield": "Please provide a text in the textfield",
            "csv_btn": "Tab in .csv"
        },
        "result": {
            "title": "Results",
            "no_result": "No result to display yet"
        }
    }

In this file lives all the keys that are displayed in the default application (see this tutorial for more information). simply change the one called in :code:`ui.ipynb` footer. as such :

.. code-block:: python 

    # component/message/en.json

    {
        # [...]
        "app": {
            # [..]
            "footer": "My new footer text"

    # [...]
        }
    }

.. warning::

    don't forget that JSON format only support " (double quote)

.. tip:: 

    if you use different translation you'll also want to change the :code:`fr.json` accordingly.


If the new footer text does not include parameters, remove the :code:`.format(2020)` in :code:`ui.ipynb` third cell.

Remove the footer 
-----------------

If the sepal footer (always included bellow dashboard app) is sufficient for your app, then you can consider removing the footer. 
first remove the :code:`app_footer` variable from the :code:`ui.ipynb` file by removing the third cell. 
Then in the penultimate cell of the same file remove the line coresponding to the footer :

.. code-block:: python 

    # build the Html final app by gathering everything 
    app = sw.App(
        tiles    = app_content, 
        appBar   = app_bar, 
        navDrawer= app_drawer
    ).show_tile('aoi_widget') # id of the tile you want to display

