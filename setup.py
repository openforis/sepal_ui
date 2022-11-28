from pathlib import Path
from subprocess import check_call

from setuptools import setup
from setuptools.command.develop import develop

version = "2.12.0"

DESCRIPTION = "Wrapper for ipyvuetify widgets to unify the display of voila dashboards in SEPAL platform"
LONG_DESCRIPTION = open("README.rst").read()


class DevelopCmd(develop):
    def run(self):
        """overwrite run command to install pre-commit hooks in dev mode"""
        check_call(["pre-commit", "install", "-t", "pre-commit", "-t", "commit-msg"])
        super().run()


def get_templates():
    """Get all the templates files from the templates and save them in the distribution"""

    root = Path(__file__).parent / "sepal_ui"
    templates = (root / "templates").rglob("*")
    ignore_files = [".ipynb_checkpoints", "__pycache__"]

    return [
        str(i.relative_to(root))
        for i in templates
        if not any([s in str(i) for s in ignore_files])
    ]


setup_params = {
    "name": "sepal-ui",
    "version": version,
    "license": "MIT",
    "license_file": "LICENSE.txt",
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
        "werkzeug<2.2.0",  # https://github.com/python-restx/flask-restx/issues/460
        "haversine",
        "ipyvue>=1.7.0",  # this is the version with the class manager
        "ipyvuetify",  # it will work anyway as the widgets are build on the fly
        "earthengine-api",
        "markdown",
        "ipyleaflet>=0.14.0",  # to have access to data member in edition
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
        "python-box",
        "xyzservices",
        "planet==2.0a2",  # this is a prerelease
        "pyyaml",
        "dask",
        "tqdm",
        "jupyter-server-proxy",
        "matplotlib",
        "rioxarray",
    ],
    "extras_require": {
        "dev": [
            "pre-commit",
        ],
        "test": [
            "coverage",
            "pytest",
            "pytest-sugar",
            "pytest-icdiff",
            "pytest-instafail",
            "nbmake ",
        ],
        "doc": [
            "docutils<0.19",  # remove once m2r2 0.3.3 is released
            "sphinx",
            "jupyter-sphinx",
            "pydata-sphinx-theme",
            "sphinx-notfound-page",
            "Sphinx",
            "sphinxcontrib-spelling",
            "sphinx-copybutton",
            "pandoc",
            "m2r2",
            "sphinxcontrib-autoprogram",
            "sphinx-favicon",
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
        "sepal_ui.planetapi",
    ],
    "package_data": {
        "sepal_ui": [
            "scripts/*.csv",
            "scripts/*.md",
            "scripts/*.json",
            "message/**/*.json",
            "bin/*",
            "frontend/css/*.css",
            "frontend/json/*.json",
            "frontend/js/*.js",
            *get_templates(),
        ]
    },
    "entry_points": {
        "console_scripts": [
            "module_deploy = sepal_ui.bin.module_deploy:main",
            "module_factory = sepal_ui.bin.module_factory:main",
            "module_l10n = sepal_ui.bin.module_l10n:main",
            "module_theme = sepal_ui.bin.module_theme:main",
            "module_venv = sepal_ui.bin.module_venv:main",
            "activate_venv = sepal_ui.bin.activate_venv:main",
            "ee_token = sepal_ui.bin.ee_token:main",
        ]
    },
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    "cmdclass": {
        "develop": DevelopCmd,
    },
}

setup(**setup_params)
