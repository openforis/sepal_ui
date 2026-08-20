Installation
============

.. note::

   `sepal-ui` has been renamed to `pysepal`. pysepal 4.0 removed the ``sepal_ui``
   compatibility package: ``import sepal_ui`` no longer works, use ``import pysepal``.

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

The source of pysepal can be installed from the `GitHub repo <https://github.com/openforis/pysepal>`_:

.. code-block:: bash

   python -m pip install git+https://github.com/openforis/pysepal.git#egg=pysepal

For local development
---------------------

.. code-block:: bash

   git clone https://github.com/openforis/pysepal.git
   cd pysepal/
   pip install -e .
