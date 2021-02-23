How to upload your module on the SEPAL dashboard ? 
==================================================

You're module is now completely ready and functionnal and you want to let everyone use your workflow, here are the few tips to send your repository to the sepal dashboard. 

Check your dependancies 
-----------------------

During your development, you may have enconter some trouble  using the preinstalled python librairies of Sepal and you decided to install new one using the terminal :

.. code-block:: bash

    $ pip install <my_lib>

As a regular Sepal user, you don't have the rights to write in the :code:`usr/` so your installation have been performed using the :code:`--user` option. All the other Sepal user thus don't have access to your lib. 
To verify that your module is still working try to lauch it using the :code:`python3 module` kernel. This kernel only use the default libs and will help you pinpoint what is missing in Sepal. 

.. tip::

    keep a list of all the missing python libs

Add documentation
-----------------

To be used by other Sepal users, your module will need to provide a complete documentation. This documetnation will be linked in the official documentation of sepal so it needs to respect some basic rules.

- use only 1 page to describe the full process 
- use the .rst standard (cheatset can be found `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html#section-structure>`_)
- make sure that the used external contents are set as absolute path

Create a release branch 
-----------------------

The sepal prod environment will be listening to the :code:`release` branch of your repository, so you need to create one. 

.. warning::

    After it's publication every push to the :code:`release` branch will be updated on the prod env so prefer to continue developing in the :code:`master` branch and merge in release only when everything is ready

Open an issue on the Sepal repository 
-------------------------------------

Everything is ready to fly so open an issue on the sepal `issue tracker <https://github.com/openforis/sepal/issues>`_ respecting the :code:`new module` template. 

You'll be asked to provide : 

- the name of the repository 
- the name of the app to display in the dashboard
- a short description of the module (1 liner)
- the missing python libs

Our maintainers will then study your request and may ask you to make modifications to your repository before pulling. 