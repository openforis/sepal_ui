from distutils.core import setup
setup(
  name = 'sepal_ui',      
  packages = ['sepal_ui'],   
  version = '0.0',   
  license='MIT',        
  description = 'wrapper for ipyvuetify widgets to unify the display of voila dashboards in the sepal plateform',   
  author = 'Pierrick Rambaud',                   
  author_email = 'pierrick.rambaud49@gmail.com',  
  url = 'https://github.com/12rambau',
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['UI', 'Python', 'widget', 'sepal'], 
  install_requires=[            # I get to this in a second
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