How to upload your module on the SEPAL dashboard? 
==================================================

Your module is now completely ready and functional and you want to let everyone use your workflow, here are the few tips to send your repository to the SEPAL dashboard. 

Check your dependencies 
-----------------------

During your development, you may have encountered some troubles using the preinstalled Python libraries of SEPAL and you have decided to install a new one using the terminal:

.. code-block:: bash

    $ pip install <my_lib>

As a regular SEPAL user, you don't have the rights to write in the :code:`/usr/` folder, so your installations have been performed using the :code:`--user` option. All the other SEPAL users thus don't have access to your libraries. 
In order to make your application work, SEPAL will create a specific virtual environment (:code:`venv`) for your application. For that purpose, you will need to update the :code:`requirements.txt` file that is held at the root of your module. By default the following content is already set:

Standard environment
^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    # These libs are requested to build common python libs
    # If you are an advanced user and you are sure to not use them, you can comment the following lines
    wheel
    Cython
    pybind11

    # if you require GDAL and or pyproj in your module please uncomment these lines
    # there are set up to be inlined with SEPAL implementation of GDAL and PROJ version
    GDAL==3.0.4
    pyproj<3.0.0

    # The base lib to run any sepal_ui based app 
    # Don't forget to fix it to a specific version when you're app is ready
    sepal_ui
    
The first three libraries are compiling tools that are usually required for common Python libraries, comment them only if you are sure that none of your libraries are using them. 

The :code:`gdal` and :code:`pyproj` libraries are working on top of the PROJ and GDAL C++ libraries that are already installed in SEPAL. The version suggested here is aligned with the current SEPAL release. If you need a specific version please let us know by sending us a request in the `issue tracker of the SEPAL repository <https://github.com/openforis/sepal/issues>`_.

sepal_ui is off course a mandatory requirement.

Customize the env
^^^^^^^^^^^^^^^^^

To customize this environment add any libraries that are useful for your module. For this purpose use the :code:`module_deploy` command. It will automatically add your dependencies to the requirements and will deal with the already known troubleshooting:

.. code-block:: console

    $ cd <my_module_path>
    $ module_deploy

    ##########################################
    #                                        #
    #      SEPAL MODULE DEPLOYMENT TOOL      #
    #                                        #
    ##########################################
    
    Welcome to the module deployment interface.
    This interface will help you prepare your module for deployment.
    Please read the documentation of the library before launching this script
    
    
    Export the env configuration of your module
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    INFO: Successfully saved requirements file in /home/prambaud/modules/sepal_ui_template/req_tmp.txt
    Removing sepal_ui from reqs, duplicated from default.
    Removing earthengine_api from reqs, included in sepal_ui.
    Removing ee from reqs, included in sepal_ui.
    sepal_ui version have been freezed to  2.0.6
    
    WARNING: The requirements.txt file have been updated. The tool does not cover every possible configuration so don't forget to check the final file before pushing to release
    
.. note::

    If you want to import a file directly from the source, use the git import syntax: 
    
    .. code-block::
    
        git+git://github.com/12rambau/sepal_ui.git#egg=sepal_ui
        
    with everything after "git+" being the ssh link to the repository and "egg=" the name used by the lib in your file. If you want to know more about this method please refer to `this blog post <https://codeinthehole.com/tips/using-pip-and-requirementstxt-to-install-from-the-head-of-a-github-branch/>`_.
    
Check your env
^^^^^^^^^^^^^^

As mentioned at the end of the command you should test your environment in SEPAL to check if everything is working. 

First, create a new **venv** anywhere in your home directory: 

.. code-block:: console

    $ python3 -m venv <path_to_venv_folder/venv_name>
    
Then activate this virtual environment: 

.. code-block:: console

    $ source <path_to_venv_folder/venv_name>/bin/activate
    (venv_name) $
    
The name in parenthesis shows to the user that the terminal is now running in a specific environment. 

.. tip::

    to return to the general environment simply run:
    
    .. code-block:: console
    
        (venv_name) $ deactivate
        $ 
        
    The parenthesis should disappear.
    
In this new environment run the following command using your requirement.txt file:

.. code-block:: console 

    $ grep -v "^#" <path-to-module>/requirements.txt | xargs -n 1 -L 1 pip3 install

It will recursively install all your libraries in the virtual env. If you are experiencing difficulties, please contact us in the `issue tracker <https://github.com/12rambau/sepal_ui/issues>`_. 

Add documentation
-----------------

To be used by other SEPAL users, your module will need to provide complete documentation. This documentation will be linked in the official documentation of SEPAL so it needs to respect some basic rules.

- Use only 1 page to describe the full process 
- Use the .rst standard (cheat-set can be found `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html#section-structure>`__)
- Make sure that the used external contents are set as an absolute path

Create a release branch 
-----------------------

The SEPAL :code:`prod` environment will be listening to the :code:`release` branch of your repository, so you need to create one. 
The SEPAL :code:`test` environment will be listening to the :code:`master` branch of the repository.

.. warning::

    After its publication every push to the :code:`release` branch will be updated on the :code:`prod` environment so prefer to continue developing in the :code:`master` branch and merge in release only when everything is ready. As the :code:`master` branch will still be listened by the :code:`test` environment, Your Beta tester will still have something to play with without sending half-finished tools to the public SEPAL website.

Open an issue on the SEPAL repository 
-------------------------------------

Everything is ready to fly so open an issue on the SEPAL `issue tracker <https://github.com/openforis/sepal/issues>`_ respecting the :code:`new module` template. 

You'll be asked to provide : 

- Name of the repository 
- Name of the app to display in the dashboard
- Short description of the module (1 liner)

Our maintainers will then study your request and may ask you to make modifications to your repository before pulling it. 

Add the documentation to sepal-doc 
----------------------------------

Now that your module is available on SEPAL you need to help the users with an adapted documentation. If you followed all the steps of these tutorials you have already created/modified the 3 :code:`.rst` files that live in the :code:`doc` folder. create a PR on the `documentation of SEPAL <https://github.com/openforis/sepal-doc>`_ following the steps described `here <https://docs.sepal.io/en/latest/team/contribute.html#new-modules>`__.

Once your PR has been accepted you should change in the ui.ipynb the link to the documentation to make it point to the page in `<https://docs.sepal.io/modules>`_:

.. code-block:: python 

    # ui.ipynb

    # !!! not mandatory !!! 
    # Add the links to the code, wiki and issue tracker of your
    code_link = 'https://github.com/<profile>/<repository>'
    wiki_link = 'https://docs.sepal.io/module/<module_name>.html'
    issue_link = 'https://github.com/<profile>/<repository>/issues/new'

.. spelling:: 

    env
