from distutils.core import setup
    
setup(
    name = 'sepal_ui',      
    packages = ['sepal_ui', 'sepal_ui.scripts'],   
    package_data={'sepal_ui': ['scripts/*.csv', 'scripts/*.md']},
    version = '0.5-beta',   
    license='MIT',        
    description = 'wrapper for ipyvuetify widgets to unify the display of voila dashboards in the sepal plateform',  
    author = 'Pierrick Rambaud',                   
    author_email = 'pierrick.rambaud49@gmail.com',  
    url = 'https://github.com/12rambau/sepal_ui',
    download_url = 'https://github.com/12rambau/sepal_ui/archive/v_0.5-beta.tar.gz',
    keywords = ['UI', 'Python', 'widget', 'sepal'], 
    install_requires=[
        'haversine',
        'ipyvuetify',
        'geemap',
        'ipyvuetify',
        'earthengine-api',
        'bqplot',
        'markdown'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.6',
    ],
)