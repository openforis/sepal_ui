How to upload your module on the SEPAL dashboard ? 
==================================================

You're module is now completely ready and functional and you want to let everyone use your workflow, here are the few tips to send your repository to the sepal dashboard. 

Check your dependencies 
-----------------------

During your development, you may have encounter some trouble  using the preinstalled python libraries of Sepal and you decided to install new one using the terminal :

.. code-block:: bash

    $ pip install <my_lib>

As a regular Sepal user, you don't have the rights to write in the :code:`usr/` so your installation have been performed using the :code:`--user` option. All the other Sepal user thus don't have access to your lib. 
To verify that your module is still working try to launch it using the :code:`python3 module` kernel. This kernel only use the default libraries and will help you pinpoint what is missing in Sepal. 

.. tip::

    keep a list of all the missing python libraries

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
- the missing python libraries

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
