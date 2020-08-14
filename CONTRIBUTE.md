# Contribute

## install the project

run the following command to start developing on the develop branch 

```bash
$ git clone https://github.com/12rambau/sepal_ui.git
$ git checkout --track origin/develop
```

## develop within the project 

Since 2020-08-14, this repository follows these [development guidelines](https://nvie.com/posts/a-successful-git-branching-model/). The git flow is thus the following
<img src="https://nvie.com/img/git-model@2x.png" height="700" />

Please consider using the `--no-ff` option when merging to keep the repository consistent with PR. 

## install  your local modification instead of the Pypi lib 

To validate you modification go to the root folder of the package and run
```py
python3 setup.py sdist
```

then install the sepal_ui from your local folder
```py
pip install [your_sepal_ui_folder]
```

> :warning: Remember that if you create modifications that alter the lib standard funtionning It will break the applications that use it on your sepal app dashboard. 
