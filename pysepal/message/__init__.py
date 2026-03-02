"""Initialization of the ``Translator`` used in the sepal-ui.

Can be accessed as:

.. code-block::

    from sepal_ui.message import ms
"""

from pathlib import Path

from sepal_ui.translator import Translator

ms = Translator(Path(__file__).parent)
