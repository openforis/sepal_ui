Installation
============

.. warning::

   `sepal-ui` is in deprecation transition and will be renamed to `pysepal`.
   This page documents the current package while migration is in progress.

.. note::

   The Sepal environment is up to date with the latest stable version of :code:`pysepal`.
   No installation is required

Stable release
--------------

Use pip to install from `Pypi <https://pypi.org/project/pysepal/>`_:

.. code-block:: bash

   pip install pysepal

From source
-----------

The source of pysepal can be installed from the `GitHub repo <https://github.com/12rambau/sepal_ui>`_:

.. code-block:: bash

   python -m pip install git+git://github.com/12rambau/sepal_ui.git#egg=pysepal

For local development
---------------------

.. code-block:: bash

   git clone https://github.com/12rambau/sepal_ui.git
   cd sepal_ui/
   pip install -e .
