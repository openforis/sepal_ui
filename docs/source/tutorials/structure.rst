Structure of a module repository 
================================

In this tutorial we will explain how the files are structured in the module and how to use each module to build an app 

If you just created you module you should have the following tree : 

.. code-block::

   ├── [app_name]
   |     |
   |     ├── component
   |     |     ├── model
   |     |     |     ├── __init__.py
   |     |     |     └── default_process_model.py
   |     |     |
   |     |     ├── message
   |     |     |     ├── __init__.py
   |     |     |     ├── en.json
   |     |     |     ├── fr.json
   |     |     |     ├── es.json
   |     |     |     └── test_translation.ipynb
   |     |     |
   |     |     ├── parameter
   |     |     |     ├── __init__.py 
   |     |     |     └── default_directory.py
   |     |     |
   |     |     ├── scripts 
   |     |     |     ├── __init__.py
   |     |     |     └── default_process.py
   |     |     |
   |     |     ├── tile 
   |     |     |     ├── __init__.py
   |     |     |     ├── default_process_tile.py
   |     |     |     └── default_result_tile.py 
   |     |     |
   |     |     └── widget
   |     |           └── __init__.py
   |     |
   |     ├── doc 
   |     |
   |     ├── utils
   |     |     └── ABOUT.md
   |     |
   |     ├── .gitignore
   |     ├── LICENCE
   |     ├── README.md
   |     |
   |     ├── about_ui.ipynb
   |     ├── aoi_ui.ipynb
   |     ├── default_process.ipynb
   |     |
   |     ├── no_ui.ipynb
   |     └── ui.ipynb


Project parameter files
-----------------------

license
^^^^^^^

By default we use a `MIT <https://opensource.org/licenses/MIT>`_ license as in all Sepal development. You'll need to customize this file to replace:

* the year
* your name/company name

If your project require a specific license file you can edit this one to reflect what you need. I strongly suggest to edit this file directly in GitHub as the website provide a number of templates

.. image:: ../_image/tutorials/structure/license-template.png

If you use a custom license, you'll nee to change the badge in the :code:`README.md`. 
copy paste any badge from this `github repository <https://gist.github.com/lukas-h/2a5d00690736b4c3a7ba>`_ instead of the classic MIT one : 

.. code-block::

   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

:code:`.gitignore`
^^^^^^^^^^^^^^^^^^

We use the default Python Github :code:`.gitignore`. It will prevent any cache file to be pushed in the GitHub repository. 
If your module requires API keys, it is strongly suggested to add the :code:`api_key.txt` file inside the :code:`.gitignore` to avoid security breaches.

README.md
^^^^^^^^^

This file will e displayed in your GitHub front page. It's useful to provide insight to people about what your module is doing.
it uses the markdown format. you can use the `offical cheatsheet <https://github.com/adam-p/markdown-here/wiki/Markdown-Here-Cheatsheet>`_ to help you refactor your README

utils
-----

You can add anything useful for your project in this folder (API code, workbench tools). at the moment it only host the ABOUT.md file. 

Partial ui
----------

* :code:`about_ui.ipynb`
* :code:`aoi_ui.ipynb`
* :code:`default_process.ipynb`

these files are partial UI file. They will be used to create each step of our app. more information in this tutorial

Final ui
--------

* :code:`no_ui.ipynb`
* :code:`ui.ipynb

Thes files are gathering all the partial ui to create a fully functional app. The :code:`ui.ipynb` file is designed to be display using voila when the :code:`no_ui.ipynb` can be launched as a simple Python Notebook.
More information in `this tutorial <#>`_ and `this tutorial <#>`_.

component
---------

In this folder live all your app logic. Everything is well split for the sake of maintenance. Python developer have already recognize the :code:`__init__.py` file in each of it's folder which means that every component is a package and can be used as such in any Python file.

model
^^^^^

In this package every :code:`Model` object that will be used in the project are gathered. 

message
^^^^^^^

In this package all the messages that will be displayed in the app are gathered in json dictionaries. More information in this tutorial

parameter 
^^^^^^^^^

For the sake of maintenance, hard-coded parameter shouldn't be used in the scripts or in the tiles. Instead they should be gathered in the parameter package. More information in this tutorial

scripts
^^^^^^^

This is where your app logic lives. More information in this tutorial.

tile
^^^^

This is where all the tiles that will be displayed in the app are created. More information in this tutorial 

.. note::

   In the :code:`sepal_ui` framework, app are designed using the tile-based UX. 
   A user interface that places icons in rows and columns with no space in between, exemplified by Windows Phone and Windows 8 Metro. we will refers to these unit as "tile" for the rest of the documentation

widget
^^^^^^

At some point you'll may encounter limitation in the basics `vuetify <https://vuetifyjs.com/en/>`_ components. every custom widget that you'll build need to live in this package. More information in this tutorial.

.. spelling::

   utils
