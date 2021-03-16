Remove the default process and tiles
====================================

When you started your module with the module, several default process and tile where already available. Now that you have implemented your own code you may want to remove these one.
The easy answer is : remove everything that starts with the :code:`default_` prefix but we will of course remove them all step by step.  

remove from UI files
-------------------- 

ui.ipynb and no_ui.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^

The first step is to remove the tiles from :code:`ui.ipynb` and :code:`no_ui.ipynb` to make sure that this called is not shown any more to the users. 
in both files, remove the following line in order to stop the importation of the default tiles

.. code-block:: python 

    %run default_process.ipynb

Now the partial ui is never loaded. in :code:`no_ui.ipnb` remove the the cells containing :code:`default_process_tile` and :code:`default_result_tile.ipynb`. 
This two variables need to be removed from the :code:`app_content`. 
Still in the :code:`ui.ipynb` notebook, remove the two :code:`DrawerItem` corresponding to our tiles and you are good to go.

partial ui 
^^^^^^^^^^

Now that we have removed every call to :code:`default_process_ui.ipynb`, we can safely remove this file 

remove components 
-----------------

The high modularity of allows to remove and add components very fast and without possible error. 

in all compoent but message (:code:`tile`, :code:`scripts`, :code:`parameter` and :code:`io`) remove all the files that are starting by the :code:`default_` prefix. 
In each package make sure that thes file are not imported by the :code:`__init__.py`. If it's still the case remove this imports

update messages 
---------------

In the message dictionnaries (:code:`en.json` and :code:`fr.json`) remove all the keys that start with the :code:`default_` prefix and their content 

going from : 

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
        "default_result": {
            "title": "Results",
            "no_result": "No result to display yet"
        }
    }

to 

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
        }
    }

.. tip::

    it's easier to do this procedure at the beggining rather than at the end of your development

