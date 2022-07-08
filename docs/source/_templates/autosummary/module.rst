{% extends "!autosummary/module.rst" %}

{% block functions -%}
{% if functions -%}
   .. rubric:: Functions

   .. autosummary::
      :toctree:
      :nosignatures:
      
      {% for item in functions -%}
      {{ item }}
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
      {{ item }}
      {% endfor -%}
{% endif -%}
{% endblock -%}