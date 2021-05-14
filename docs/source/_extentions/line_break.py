# -*- coding: utf-8 -*-

"""
ReST directive for creating line break in your documentation when needed.
The directive does note require any argument.
Example::
    .. line-break::
"""
from docutils import nodes
from docutils.parsers.rst import Directive, directives

class LineBreak(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    html = "<br/>"
    
    def run(self):
        return [nodes.raw('', self.html, format='html')]
    
def setup(builder):
    directives.register_directive('line-break', LineBreak)
        