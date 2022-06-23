Contributing guidelines
=======================

.. warning::

    Remember that if you create modifications that alter the lib standard functioning It will break the applications that use it on the SEPAL app dashboard. 

After forking the projet, run the following command to start developing: 

.. code-block:: console

    $ git clone https://github.com/<github id>/sepal_ui.git
    $ cd sepal_ui 
    $ pip install -e .[dev, test, doc]
    
.. danger:: 

    :code:`pre-commits` are installed in edit mode. Every commit that does not respect the conventional commits framework will be refused. 
    you can read this `documentation <https://www.conventionalcommits.org/en/v1.0.0/>`_ to learn more about them and we highly recommend to use the :code:`commitizen` lib to create your commits: `<https://commitizen-tools.github.io/commitizen>`_.
    
Participate to translation
--------------------------

The tool is currently tranlated in the following languages: 

.. csv-table::

    English, Français, Español

You can contribute to the translation effort on our `pontoon project <https://sepal-ui-translation.herokuapp.com/projects/sepal-ui/>`__. Contributors can suggest new languages and new translation. The admin will review this modification as fast as possible. If nobody in the core team master the suggested language, we'll be force to trust you !


Develop within the project
--------------------------

Since 2020-08-14, this repository follows these `development guidelines <https://nvie.com/posts/a-successful-git-branching-model/>`_. The git flow is thus the following:

.. figure:: https://nvie.com/img/git-model@2x.png
    :alt: the Git branching model 
    :width: 70%
    
    The git branching model

Please consider using the :code:`--no-ff` option when merging to keep the repository consistent with PR. 

In the project to adapt to :code:`JupyterLab` IntelSense, we decided to explicitly write the `return` statement for every function.

As we are holding a single documentation page, we need to provide the users with version informations. When a new function or class is created please use the `Deprecated <https://pypi.org/project/Deprecated/>`__ lib to specify that the feature is new in the documentation. 

.. code-block:: python

    from deprecated.sphinx import deprecated
    from deprecated.sphinx import versionadded
    from deprecated.sphinx import versionchanged


    @versionadded(version='1.0', reason="This function is new")
    def function_one():
        '''This is the function one'''


    @versionchanged(version='1.0', reason="This function is modified")
    def function_two():
        '''This is the function two'''


    @deprecated(version='1.0', reason="This function will be removed soon")
    def function_three():
        '''This is the function three'''
    
How to commit
-------------

In this repository we use the Conventional Commits specification.
The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with SemVer, by describing the features, fixes, and breaking changes made in commit messages.

You can learn more about Conventional Commits following this `link <https://www.conventionalcommits.org/en/v1.0.0/>`_

What can I push and where
-------------------------

Our branching system embed some rules to avoid crash of the production environment. If you want to contribute to this framework, here are some basic rules that we try our best to follow :

-   the modification you offer is solving a critical bug in prod : **PR in hotfix**
-   the modification you propose solve the following issues : test, documentation, typo, quality, refactoring, translation **PR in master**
-   the modification you propose is a new feature : open an issue to discuss with the maintainers and then **PR to develop**

the maintainers will try their best to use PR for new features, to help the community follow the development, for other modification they will simply push to the appropriate branch

Create a new release
--------------------

.. danger:: 

    for maintainers only 
    
 .. warning::
 
     You need to use the :code:`commitizen` lib to create your release: `<https://commitizen-tools.github.io/commitizen>`_
    
In the files change the version number by runnning commitizen `bump`: 

.. code-block:: console

    cz bump

It should modify for you the version number in :code:`sepal_ui/__init__.py`, :code:`setup.py`, and :code:`.cz.yaml` according to sementic versionning thanks to the conventional commit that we use in the lib. 

It will also update the :code:`CHANGELOG.md` file with the latest commits, sorted by categories if you run the following code, using the version bumped in the previous commit.

.. code-block:: console 

    cz changelog --unreleased-version="v_x.x.x"

Then push the current :code:`master` branch to the :code:`release` branch. You can now create a new tag with your new version number. use the same convention as the one found in :code:`.cz.yaml`: :code:`v_$minor.$major.$patch$prerelease`.

.. warning::

    The target branch of the new release is :code:`release` not :code:`master`. 
    
The CI should take everything in control from here and execute the :code:`Upload Python Package` GitHub Action that is publishing the new version on `PyPi <https://badge.fury.io/py/sepal-ui>`_.
    
Once it's done you need to trigger the rebuild of SEPAL. modify the following `file <https://github.com/openforis/sepal/blob/master/modules/sandbox/docker/script/init_sepal_ui.sh>`_ with the latest version number and the rebuild will start automatically. 


Setting ENV variables
---------------------

Sometimes is useful to create enviromental variables to store some data that your workflows will receive (i.e. component testing). For example, to perform the local tests of the :code:`planetapi` sepal module, the :code:`PLANET_API_KEY` and :code:`PLANET_API_CREDENTIALS` env vars are required, even though they are also skippable.

To store a variable in your local session, just type :code:`export=` followed by the var value.

.. code-block:: console 

    $ export PLANET_API_KEY="neverending_resourcesapi"
    
However, this variable will expire everytime you start a new session, to create it every session and make it live longer, go to your :code:`home` folder and save the previous line in the :code:`.bash_profile` file.
    
.. code-block:: console 

    $ vim .bash_profile

.. note::
    The current enviromental keys and its structure is the following:

    - PLANET_API_CREDENTIALS: '{"username": "user@neim.com", "password": "secure"}'
    - PLANET_API_KEY: "string_planet_api_key"

.. spelling:: 

    pre
