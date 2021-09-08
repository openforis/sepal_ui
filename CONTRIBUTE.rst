Contribute
----------

run the following command to start developing on the develop branch 

.. code-block:: console

    $ git clone https://github.com/12rambau/sepal_ui.git
    $ git checkout --track origin/develop
    
Activate the pre-commit
=======================

The project embed some git hooks that allows better CI and improve code quality. To activate them, please follow these few steps: 

Before you can run hooks, you need to have the pre-commit package manager installed.

.. code-block:: console

    $ pip install pre-commit
    
Then install the git hook scripts by running pre-commit install to set up the git hook scripts:

.. code-block:: console

    $ pre-commit install
    $ pre-commit install --hook-type commit-msg
    
Now :code:`pre-commit` will run automatically on :code:`git commit` !

.. danger:: 

    Now that the :code:`pre-commits` are installed, every commit that does not respect the conventional commits framework will be refused. 
    you can read this `documentation <https://www.conventionalcommits.org/en/v1.0.0/>`_ to learn more about them and we highly recommend to use the :code:`commitizen` lib to create your commits: `https://commitizen-tools.github.io/commitizen`_.

Develop within the project
==========================

Since 2020-08-14, this repository follows these `development guidelines <https://nvie.com/posts/a-successful-git-branching-model/>`_. The git flow is thus the following:

.. figure:: https://nvie.com/img/git-model@2x.png
    :alt: the Git branching model 
    :width: 70%
    
    The git branching model

Please consider using the :code:`--no-ff` option when merging to keep the repository consistent with PR. 

In the project to adapt to :code:`JupyterLab` IntelSense, we decided to explicitly write the `return` statement for every function.

Install  your local modification instead of the Pypi lib 
========================================================

To validate you modification go to the root folder of the package and run:

.. code-block:: console

    $ python3 setup.py sdist


then install the sepal_ui from your local folder:

.. code-block:: console

    $ pip install -e [your_sepal_ui_folder]

.. warning::

    Remember that if you create modifications that alter the lib standard functioning It will break the applications that use it on the SEPAL app dashboard. 
    
How to commit
=============

In this repository we use the Conventional Commits specification.
The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with SemVer, by describing the features, fixes, and breaking changes made in commit messages.

You can learn more about Conventional Commits following this `link <https://www.conventionalcommits.org/en/v1.0.0/>`_

What can I push and where
=========================

Our branching system embed some rules to avoid crash of the production environment. If you want to contribute to this framework, here are some basic rules that we try our best to follow :

-   the modification you offer is solving a critical bug in prod : **PR in hotfix**
-   the modification you propose solve the following issues : test, documentation, typo, quality, refactoring, translation **PR in master**
-   the modification you propose is a new feature : open an issue to discuss with the maintainers and then **PR to develop**

the maintainers will try their best to use PR for new features, to help the community follow the development, for other modification they will simply push to the appropriate branch

Create a new release
--------------------

.. danger:: 

    for maintainers only 
    
In the files change the version number in the following file: :code:`VERSION`

Then push the current master branch to the release branch. You can now create a new tag with your new version number. use the same convention as the one found in :code:`setup.py`.

.. warning::

    The target branch of the new release is :code:`release` not :code:`master`. 
    
Now publish the new version of the lib on Pypi : 

.. code-block:: console

    $ cd sepal_ui
    $ python setup.py sdist
    $ twine upload dist/sepal_ui-<version number>.tar.gz
    
Once it's done you need to trigger the rebuild of SEPAL. modify the following `file <https://github.com/openforis/sepal/blob/master/modules/sandbox/docker/script/init_sepal_ui.sh>` with the latest version number and the rebuild will start automatically. 

.. spelling:: 

    pre
