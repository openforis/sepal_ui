# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

# General information about the project.
project = 'sepal-ui'
copyright = f"2020-{datetime.now().year}, the sepal development team"
author = 'Pierrick Rambaud'

# The full version, including alpha/beta/rc tags
release = '1.0.2'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', 'pydata_sphinx_theme']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_logo = os.path.abspath('../img/sepal.png') 
html_favicon = os.path.abspath('../img/favicon.ico')
html_theme_options = {
    #"external_links": [],
    "github_url": "https://github.com/12rambau/sepal_ui",
    "use_edit_page_button": True,
    #"twitter_url": "https://twitter.com/pandas_dev"
}
html_context = {
    "github_user": "12rambau",
    "github_repo": "sepal_ui",
    "github_version": "master",
    "doc_path": "docs/source",
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']