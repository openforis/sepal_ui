How to deploy on the web
========================

.. image:: https://pythonforundergradengineers.com/posts/voila/images/jupyter_voila_heroku.png
    :alt: setup image
    :target: https://pythonforundergradengineers.com/deploy-jupyter-notebook-voila-heroku.html
    :width: 100 %

First of all, note that we are sad that you won't consider deploying your app on the SEPAL platform, but as the :code:`sepal-ui` framework is platform agnostic, we'll also demonstrate how to create and deploy an app on the web using `Heroku <https://dashboard.heroku.com/apps>`__. 

This tutorial has been inspired by: `<https://pythonforundergradengineers.com/deploy-jupyter-notebook-voila-heroku.html>`__

.. note:: 

    This methodology have been used to deploy the `demo app <https://sepal-ui.herokuapp.com>`__ of the framework. the source code can be found `here <https://github.com/12rambau/sepal_ui_template/tree/heroku>`__.

.. warning::

    -   Heroku is a cloub hosting platform where deploying an app on a public account is free. If you prefer to use your own favorite service, you'll need to adapt this tutorial. You can still reach the development team in the `issue tracker <https://github.com/12rambau/sepal_ui/issues>`__ if you are experiencing difficulties.
    -   The web platform offered by Heroku have very limited computation power. Please consider deploying to SEPAL if you require powerfull computation resources.
    
.. danger::

    As of now the applications based on Google Earth Engine cannot work outside of SEPAL as it's impossible to register to their services. An `issue <https://github.com/12rambau/sepal_ui/issues/336>`__ has been oppened, have a look if you require this feature.
    
Set up the app
--------------

Create
******

To start this tutorial let's create an application that doesn't require GEE and runs only on Python tools. For the example, we'll use the default template that only include a GADM baed Aoi selector. The full process is described in the `Create my first module <./create-module.html>`__ section.

.. code-block:: console

    module_factory 
    
Using as parameters: 

-   A module name
-   An empty github url 
-   any description
-   Template function: :code:`no`
-   Need aoi selector: :code:`yes`
-   Need GEE: :code:`no`
    
.. code-block:: console

    ##################################
    #                                #
    #      SEPAL MODULE FACTORY      #
    #                                #
    ##################################

    Welcome in the module factory interface.
    This interface will help you building a dashboard app based on the sepal_ui library
    Please read the documentation of the library before launching this script



    Initializing module creation by setting up your module parameters
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

    Provide a module name: 
    test_sepal
    Provide the URL of an empty github repository: 
    git@github.com:12rambau/test_sepal.git
    Provide a short description for your module(optional): 

    Do you need to use the default function as a template [y]? 
    no
    Do you need an AOI selector in your module (it will still be possible to add one afterward) [y]? 
    yes
    Do you need a connection to GEE in your module (it will still be possible to add one afterward) [y]? 
    no

    Build the module init configuration
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

    [...]
    
Register libs
*************

To be working the app needs to have an up-to-date :code:`requirements.txt` file. to create and populate it, run the following command from within the app folder.

.. code-block:: console

    $ cd test_sepal
    ~/test_sepal$ testmodule_deploy
    
You will get the following file: 

.. code-block::

    # these libs are requested to build common python libs 
    # if you are an advance user and are sure to not use them you can comment the following lines
    wheel
    Cython
    pybind11
    pre-commit

    # if you require GDAL and or pyproj in your module please uncomment these lines
    # there are set up to be inlined with SEPAL implementation of GDAL and PROJ version
    GDAL==3.0.4
    pyproj<3.0.0

    # the base lib to run any sepal_ui based app 
    # don't forget to fix it to a specific version when you're app is ready
    sepal_ui==2.4.0


    # custom libs

Deploy on heroku
----------------

.. note::

    This deployment can be done using the Heroku CLI but it's not installed on SEPAL so we will show how to do it using the web interface
    
Now that we have a working and tested application let's begin its transformation into a working web app. Your application repository need adjustments to be compatible with the Heroku deploying environment. 

change requirements 
******************* 

The :code:`requirements.txt` created with the :code:`model_deploy` command is fully compatible with the current SEPAL environment. It needs some adjustment to be compatible with Heroku's. remove all lines refering to GDAL and PROJ installation, as they will be handled from the web interface. The final file should look like the following: 

.. code-block::

    # these libs are requested to build common python libs 
    # if you are an advance user and are sure to not use them you can comment the following lines
    wheel
    Cython
    pybind11
    pre-commit

    # the base lib to run any sepal_ui based app 
    # don't forget to fix it to a specific version when you're app is ready
    sepal_ui==2.4.0


    # custom libs
    
create runtime
**************

At the root of your repository create a :code:`runtime.txt` file containing the python version you want to use. Inside the file, just one line of text is needed. Note the lowercase python and the dash :code:`-`. The list of Heroku's supported versions can be found `here <https://devcenter.heroku.com/articles/python-support#supported-runtimes>`__.
In this case we'll use **3.8.12**: 

.. code-block::

    python-3.8.12
    
create Procfile
***************

The last required file for our Heroku deployment is a Procfile. This file includes the instructions for Heroku to deploy our app. Create a new file named :code:`Procfile` (no extension) and include the text below:

.. code-block::

    web: voila --port=$PORT --no-browser ui.ipynb
    
.. tip::

    You can change the name of the root file, if the entry point of your app is not the default :code:`ui.ipynb`
    
set the deployment env
**********************

.. warning::

   All the preiously created files need to be up-to-date on GitHub before going on the Heroku web interface.
    
From your Heroku dashboard click on :guilabel:`new` -> :guilabel:`Create new app` and follow the initial instructions (**app-name** and **region**). You can then click on :guilabel:`create app`. 

.. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/heroku/docs/img/tutorials/send-to-heroku/heroku_init.png
    :alt: heroku init
    
Then fill the following parameters in the user interface: 

-   **deployment method:** Use the github method
-   **App connected to github:** Find your repository name in the provided list clicking on :guilabel:`search`.
-   choose **automatic** or **manual** deploy. In both cases we higly suggest to use the :code:`release` branch. 

.. warning:: 

    Do not build it yet it's going to crash.
    
.. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/heroku/docs/img/tutorials/send-to-heroku/heroku_deploy.png
    :alt: heroku deploy
    
Now we need to setup the GIS environment of the app. Go to :guilabel:`settings` and then :guilabel:`add buildpack`.

There are 2 required buildpack to use for this app. First the official Python buildpack (simply click on :guilabel:`Python`) and the the GDAL/PROJ buildpack using this link: `<https://github.com/heroku/heroku-geo-buildpack.git>`__.

.. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/heroku/docs/img/tutorials/send-to-heroku/buildpacks.png
    :alt: buildpacks list
    
Now you are ready to build your app, click on :guilabel:`deploy` at the bottom of the "deploy" tab.

At the very bottom of your build log you'll find the web url that renders your app.

.. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/heroku/docs/img/tutorials/send-to-heroku/build_log.png
    :alt: buildpacks list
    
.. important::

    Congratulation you've build your first :code:`sepal-ui` based app on Heroku! 

    



    

    
    

    
    

    
    


    