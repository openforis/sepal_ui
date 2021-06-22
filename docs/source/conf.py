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
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

# General information about the project.
project = 'sepal-ui'
copyright = f"2020-{datetime.now().year}, the sepal development team"
author = 'Pierrick Rambaud'

# The full version, including alpha/beta/rc tags
release = '2.0.6'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_copybutton',
    'nbsphinx',
    'sphinx.ext.napoleon',
    'notfound.extension', 
    'sphinxcontrib.spelling',
    '_extentions.video',
    '_extentions.line_break'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['**.ipynb_checkpoints/']

# -- Load the images from the master sepal-doc -------------------------------
from urllib.request import urlretrieve

urlretrieve ('https://raw.githubusercontent.com/openforis/sepal-doc/master/docs/source/img/sepal.png', '../img/dwn/sepal.png')
urlretrieve ('https://raw.githubusercontent.com/openforis/sepal-doc/master/docs/source/img/favicon.ico', '../img/dwn/favicon.ico')
urlretrieve ('https://raw.githubusercontent.com/openforis/sepal-doc/master/docs/source/img/404-compass.png', '../img/dwn/404-compass.png')


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_logo = '../img/dwn/sepal.png'
html_favicon = '../img/dwn/favicon.ico'
html_last_updated_fmt = ''
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/12rambau/sepal_ui",
            "icon": "fab fa-github"
        },
        {
            "name": "Pypi",
            "url": "https://pypi.org/project/sepal-ui/",
            "icon": "fab fa-python",
        }
    ],
    "use_edit_page_button": True,
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
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ['css/custom.css', 'css/icon.css']

# -- Options for spelling output -------------------------------------------------
spelling_lang='en_US'
spelling_show_suggestions=True
spelling_filters = ['_filters.names.Names']
spelling_word_list_filename=[str(Path(__file__).parent.joinpath('_spelling', 'en_US.txt'))]
spelling_verbose=False
spelling_exclude_patterns=['modules/*']
