Installation
============

.. note::

   The Sepal environment is up to date with the latest stable version of :code:`sepal_ui`. 
   No installation is required 
   
Install GDAL
------------

:code:`sepal-ui` require gdal to build the vrt from downloaded images. Until we 
find a way to only rely on :code:`rasterio`, users will be force to install GDAL 
on their environment. 

.. note:: 
    
    The following is coming from the 
    `localTileServer documentation <https://localtileserver.banesullivan.com/installation/index.html#a-brief-note-on-installing-gdal>`__ 
    where they provide a nice insight on installing GDAL.
    
GDAL can be a pain in the 🍑 to install, so you may want to handle GDAL
before installing ``localtileserver`` when using ``pip``.

If on linux, I highly recommend using the `large_image_wheels <https://github.com/girder/large_image_wheels>`_ from Kitware.

.. code:: bash

   pip install --find-links=https://girder.github.io/large_image_wheels --no-cache GDAL


Otherwise, *one does not simply pip install GDAL*. You will want to either use
conda or install GDAL using your system package manager (e.g.: apt, Homebrew, etc.)

.. image:: https://raw.githubusercontent.com/banesullivan/localtileserver/main/imgs/pip-gdal.jpg
   :alt: One does not simply pip install GDAL
   :align: center

Stable release 
--------------

Use pip to install from `Pypi <https://pypi.org/project/sepal-ui/>`_:

.. code-block:: bash
   
   pip install sepal-ui

From source
-----------

The source of sepal_ui can be installed from the `GitHub repo <https://github.com/12rambau/sepal_ui>`_:

.. code-block:: bash

   python -m pip install git+git://github.com/12rambau/sepal_ui.git#egg=sepal_ui 
   
For local development
---------------------

.. code-block:: bash

   git clone https://github.com/12rambau/sepal_ui.git
   cd sepal_ui/
   pip install -e .


