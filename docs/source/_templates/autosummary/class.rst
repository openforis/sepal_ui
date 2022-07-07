{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block attributes -%}
    {% if attributes -%}
    .. rubric:: {{ _('Attributes') }}

    .. autosummary::

       {% for item in attributes -%}
       ~{{ name }}.{{ item }}
       {% endfor -%}
    {% endif -%}
    {% endblock -%}

    {% block methods -%}
    {% if methods %}
    .. rubric:: {{ _('Methods') }}

    .. autosummary::
       :nosignatures:
       
       {% for item in methods -%}
       ~{{ name }}.{{ item }}
       {% endfor -%}
    {% endif -%}
    {% endblock -%}
    
{% block details %}
{% if methods -%}
{% for item in methods  if item not in inherited_members -%}
.. autofunction:: {{ module }}.{{ objname }}.{{ item }}
{% endfor -%}
{% endif -%}
{% endblock -%}