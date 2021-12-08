from setuptools import setup
from setuptools.command.develop import develop
from subprocess import check_call

version = "2.5.3"

DESCRIPTION = "Wrapper for ipyvuetify widgets to unify the display of voila dashboards in SEPAL platform"
LONG_DESCRIPTION = open("README.rst").read()


class DevelopCmd(develop):
    def run(self):
        """overwrite run command to install pre-commit hooks in dev mode"""
        check_call(["pre-commit", "install"])
        super().run()


setup_params = {
    "name": "sepal-ui",
    "version": version,
    "license": "MIT",
    "description": DESCRIPTION,
    "long_description": LONG_DESCRIPTION,
    "long_description_content_type": "text/x-rst",
    "author": "Pierrick Rambaud",
    "author_email": "pierrick.rambaud49@gmail.com",
    "url": "https://github.com/12rambau/sepal_ui",
    "download_url": f"https://github.com/12rambau/sepal_ui/archive/v_{version}.tar.gz",
    "keywords": ["UI", "Python", "widget", "sepal"],
    "python_requires": ">=3.6.9",
    "install_requires": [
        "haversine",
        "ipyvue>=1.7.0",  # this is the version with the class manager
        "ipyvuetify",  # it will work anyway as the widgets are build on the fly
        "geemap==0.8.9",
        "earthengine-api",
        "markdown",
        "xarray_leaflet",
        "shapely",
        "geopandas",
        "pandas",
        "deepdiff",
        "colorama",
        "Deprecated",
        "Unidecode",
        "natsort",
        "pipreqs",
        "cryptography",
    ],
    "extras_require": {
        "dev": [
            "pre-commit",
        ],
        "test": [
            "coverage",
            "pytest",
        ],
        "doc": [
            "jupyter-sphinx @ git+git://github.com/jupyter/jupyter-sphinx.git",
            "pydata-sphinx-theme",
            "sphinx-notfound-page",
            "Sphinx",
            "sphinxcontrib-spelling",
            "sphinx-copybutton",
            "pandoc",
        ],
    },
    "packages": [
        "sepal_ui",
        "sepal_ui.scripts",
        "sepal_ui.frontend",
        "sepal_ui.sepalwidgets",
        "sepal_ui.aoi",
        "sepal_ui.message",
        "sepal_ui.mapping",
        "sepal_ui.translator",
        "sepal_ui.model",
        "sepal_ui.reclassify",
    ],
    "package_data": {
        "sepal_ui": [
            "scripts/*.csv",
            "scripts/*.md",
            "scripts/*.json",
            "message/*.json",
            "bin/*",
        ]
    },
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    "cmdclass": {
        "develop": DevelopCmd,
    },
}

setup(**setup_params)
