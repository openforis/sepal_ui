"""
    ReST directive for embedding deprecated admonitions (https://pypi.org/project/Deprecated/)
    There are 3 directives added: ``deprecated``, ``versionadded`` and ``versionchanged``. The only argument is the version number.
    Example::
        .. deprecated:: 1.1.0
            
            will be removed soon
"""
from __future__ import absolute_import
from docutils import nodes
from docutils.parsers.rst import Directive, directives


class Admonition(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    html = """
        <div class="admonition %(type)">
            <p class="admonition-title">
                %(text) version %(version)
            </p>
        </div>
    """

    def run(self):
        self.option["version"] = directives.uri(self.arguments[0])

        return [nodes.raw("", self.html % self.options, format="html")]


class Deprecated(Admonition):
    options = {"type": "danger", "text": "Deprecated since"}


class VersionAdded(Admonition):
    options = {"type": "tip", "text": "Added in"}


class VestionChanged(Admonition):
    options = {"type": "warning", "text": "changed in"}


def setup(builder):
    directives.register_directive("deprecated", Deprecated)
    directives.register_directive("versionadded", VersionAdded)
    directives.register_directive("versionchanged", VersionChanged)
