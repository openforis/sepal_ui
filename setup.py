from distutils.core import setup
    
setup(
    name = 'sepal_ui',      
    packages = ['sepal_ui', 'sepal_ui.scripts', 'sepal_ui.frontend', 'sepal_ui.sepalwidgets', 'sepal_ui.aoi', 'sepal_ui.message'],   
    package_data={'sepal_ui': ['scripts/*.csv', 'scripts/*.md', 'message/*.json']},
    version = '1.0.2',   
    license='MIT',        
    description = 'Wrapper for ipyvuetify widgets to unify the display of voila dashboards in SEPAL platform',  
    author = 'Pierrick Rambaud',                   
    author_email = 'pierrick.rambaud49@gmail.com',  
    url = 'https://github.com/12rambau/sepal_ui',
    download_url = 'https://github.com/12rambau/sepal_ui/archive/v_1.0.2.tar.gz',
    keywords = ['UI', 'Python', 'widget', 'sepal'], 
    install_requires=[
        'haversine',
        'ipyvuetify',
        'geemap',
        'earthengine-api',
        'bqplot',
        'markdown',
        'xarray_leaflet',
        'shapely',
        'geopandas',
        'pandas',
        'coverage',
        'deepdiff'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.6',
    ],
)