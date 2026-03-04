"""Initialization of the ``Translator`` used in pysepal.

Can be accessed as:

.. code-block::

    from pysepal.message import ms
"""

from pathlib import Path

from pysepal.translator import Translator

ms = Translator(Path(__file__).parent)
