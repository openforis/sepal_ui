{% extends "!autosummary/module.rst" %}

{% block functions -%}
{% if functions -%}
.. rubric:: Functions

.. autosummary::
   :toctree:
   :nosignatures:

   {% for item in functions -%}
   {% if item not in inherited_members -%}
   {{ item }}
   {% endif -%}
   {% endfor -%}

{% endif -%}
{% endblock -%}

{% block classes -%}
{% if classes -%}
.. rubric:: Classes

.. autosummary::
   :toctree:
   :template: autosummary/class.rst

   {% for item in classes -%}
   {% if item not in inherited_members -%}
   {{ item }}
   {% endif -%}
   {% endfor -%}

{% endif -%}
{% endblock -%}
