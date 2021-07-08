How to upload your module on the SEPAL dashboard ? 
==================================================

You're module is now completely ready and functional and you want to let everyone use your workflow, here are the few tips to send your repository to the sepal dashboard. 

Check your dependencies 
-----------------------

During your development, you may have encounter some trouble  using the preinstalled python libraries of Sepal and you decided to install new one using the terminal :

.. code-block:: bash

    $ pip install <my_lib>

As a regular Sepal user, you don't have the rights to write in the :code:`/usr/` folder so your installations have been performed using the :code:`--user` option. All the other Sepal user thus don't have access to your libs. 
in order to make your application work, Sepal will create a specific virtual environment (:code:`venv`) for your specific application. for that purpose you need to update the :code:`requirements.txt` file that is hold at the root of your module. By default the following content is already set: 

Standard environment
^^^^^^^^^^^^^^^^^^^^
.. code-block:: console

    # these libs are requested to build common python libs 
    # if you are an advance user and are sure to not use them you can comment the following lines
    wheel
    Cython
    pybind11

    # if you require GDAL and or pyproj in your module please uncomment these lines
    # there are set up to be inlined with SEPAL implementation of GDAL and PROJ version
    GDAL==3.0.4
    pyproj<3.0.0

    # the base lib to run any sepal_ui based app 
    # don't forget to fix it to a specific version when you're app is ready
    sepal_ui
    
The 3 first libs are compiling tools that are usually required for common Python libs, comment them only if you are sure that none of your libs are using them. 

The gdal and pyproj libs are working on top of the PROJ and GDAL C++ libs that are already installed in SEPAL. The version suggested here are inlined with the current SEPAL release. If you need a specific version please let us know by sending us a request in the `issue tracker of the SEPAL repository <https://github.com/openforis/sepal/issues>`_.

Sepal_ui is off course a mandatory requirements.

Customize the env
^^^^^^^^^^^^^^^^^

To customize this environment add any libs that are useful for your module. For this purpose use the :code:`module_deploy` command. it will automatically add your dependencies to the requirements and deal with the already known troubleshoutings:

.. code-block:: console

    $ cd <my_module_path>
    $ module_deploy

    ##########################################
    #                                        #
    #      SEPAL MODULE DEPLOYMENT TOOL      #
    #                                        #
    ##########################################
    
    Welcome in the module deployment interface.
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

Check your env
^^^^^^^^^^^^^^

As mentioned at the end of the the command you should test your environment in sepal to check if everything is working. 

first create a new **venv** anywhere in your home directory: 

.. code-block:: console

    $ python3 -m venv <path_to_venv_folder/venv_name>
    
Then activate this virtual environment: 

.. code-block:: console

    $ source <path_to_venv_folder/venv_name>/bin/activate
    (venv_name) $
    
the name in parenthesis show to the user that the terminal is now running in a specific environment. 

.. tips::

    to return to the general environment simply run:
    
    .. cod-block:: console
    
        (venv_name) $ deactivate
        $ 
        
    The parenthesis should disapear.
    
in this new environment run the following command using your requirement.txt file:

.. code-block:: console 

    $ grep -v "^#" <path-to-module>/requirements.txt | xargs -n 1 -L 1 pip3 install

It will recursivelly install all your libs in the virtual env. If you are expeincing difficulties, please contact us in the `issue tracker <https://github.com/12rambau/sepal_ui/issues>`_. 

Add documentation
-----------------

To be used by other Sepal users, your module will need to provide a complete documentation. This documentation will be linked in the official documentation of sepal so it needs to respect some basic rules.

- use only 1 page to describe the full process 
- use the .rst standard (cheat-set can be found `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html#section-structure>`_)
- make sure that the used external contents are set as absolute path

Create a release branch 
-----------------------

The SEPAL :code:`prod` environment will be listening to the :code:`release` branch of your repository, so you need to create one. 
The SEPAL :code:`test` environment will be listening to the :code:`master` branch of the repository.

.. warning::

    After it's publication every push to the :code:`release` branch will be updated on the :code:`prod` environment so prefer to continue developing in the :code:`master` branch and merge in release only when everything is ready. As the :code:`master` branch will still be listened by the :code:`test` environment, Your Beta tester will still have something to play with without sending half finished tools to the public SEPAL website.

Open an issue on the Sepal repository 
-------------------------------------

Everything is ready to fly so open an issue on the sepal `issue tracker <https://github.com/openforis/sepal/issues>`_ respecting the :code:`new module` template. 

You'll be asked to provide : 

- the name of the repository 
- the name of the app to display in the dashboard
- a short description of the module (1 liner)

Our maintainers will then study your request and may ask you to make modifications to your repository before pulling. 

Add the documentation to sepal-doc 
----------------------------------

Now that your module is available on SEPAL you need help the users with an adapted documentation. If you followed all the steps of these tutorials you have already created/modified the 3 :code:`.rst` files that live in the :code:`doc` folder. create a PR on the `documentation of SEPAL <https://github.com/openforis/sepal-doc>`_ following the steps described here: `<https://docs.sepal.io/en/latest/team/contribute.html#new-modules>`_.

Once your PR have been accepted you should change in the ui.ipynb the link to the documentation to make it point to the page in `<https://docs.sepal.io/modules>`_:

.. code-block:: python 

    # ui.ipynb

    # !!! not mandatory !!! 
    # Add the links to the code, wiki and issue tracker of your
    code_link = 'https://github.com/<profile>/<repository>'
    wiki_link = 'https://docs.sepal.io/module/<module_name>.html'
    issue_link = 'https://github.com/<profile>/<repository>/issues/new'
