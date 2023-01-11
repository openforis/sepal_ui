# -*- coding: utf-8 -*-


from docutils import nodes
from docutils.parsers.rst import Directive, directives


class LineBreak(Directive):
    """
    ReST directive for creating line break in your documentation when needed.

    The directive does note require any argument.

    Example:
    .. line-break::
    """

    has_content: bool = False
    "directive have no content"

    required_arguments: int = 0
    "directive have no arguments"

    optional_arguments: int = 0
    "directive have no optional arguments"

    final_argument_whitespace: bool = False
    "directive have no whitspaces between arguments"

    option_spec: dict = {}
    "no option specs"

    html: str = "<br/>"
    "the html code to inject in the output"

    def run(self) -> list:
        return [nodes.raw("", self.html, format="html")]


def setup(builder) -> None:
    directives.register_directive("line-break", LineBreak)
