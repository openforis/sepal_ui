from pkg_resources import parse_requirements
from setuptools import setup
from setuptools.command.develop import develop

version = "2.4.0"

DESCRIPTION = "Wrapper for ipyvuetify widgets to unify the display of voila dashboards in SEPAL platform"
LONG_DESCRIPTION = open("README.rst").read()
REQUIREMENTS = [str(r) for r in parse_requirements(open("requirements.txt").read())]


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
    "install_requires": REQUIREMENTS,
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
            "bin/module_factory",
            "bin/module_deploy",
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
}

setup(**setup_params)
