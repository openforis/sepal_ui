from distutils.core import setup
from pathlib import Path

version = "2.4.0"

setup(
    name="sepal-ui",
    packages=[
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
    package_data={
        "sepal_ui": [
            "scripts/*.csv",
            "scripts/*.md",
            "scripts/*.json",
            "message/*.json",
            "bin/module_factory",
        ]
    },
    python_requires=">=3.6.9",
    version=version,
    license="MIT",
    description="Wrapper for ipyvuetify widgets to unify the display of voila dashboards in SEPAL platform",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Pierrick Rambaud",
    author_email="pierrick.rambaud49@gmail.com",
    url="https://github.com/12rambau/sepal_ui",
    download_url=f"https://github.com/12rambau/sepal_ui/archive/v_{version}.tar.gz",
    keywords=["UI", "Python", "widget", "sepal"],
    install_requires=[
        "haversine",
        "ipyvue>=1.7.0",  # this is the version with the class manager
        "ipyvuetify",  # it will work anyway as the widgets are build on the fly
        "geemap",
        "earthengine-api @ git+git://github.com/openforis/earthengine-api.git@v0.1.270#egg=earthengine-api&subdirectory=python",
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
        "pre-commit",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
