from distutils.core import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()
    
setup(
    name = 'sepal_ui',      
    packages = ['sepal_ui'],   
    version = '0.0',   
    license='MIT',        
    description = 'wrapper for ipyvuetify widgets to unify the display of voila dashboards in the sepal plateform',  
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = 'Pierrick Rambaud',                   
    author_email = 'pierrick.rambaud49@gmail.com',  
    url = 'https://github.com/12rambau/sepal_ui',
    download_url = 'https://github.com/12rambau/sepal_ui/archive/v_0.1-alpha.tar.gz',
    keywords = ['UI', 'Python', 'widget', 'sepal'], 
    install_requires=[
        'haversine',
        'ipyvuetify',
        'geemap',
        'ipyvuetify',
        'ee',
        'bqplot',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.6',
    ],
)