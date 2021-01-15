# sepal_ui
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/sepal-ui.svg)](https://badge.fury.io/py/sepal-ui)
[![Build Status](https://travis-ci.com/12rambau/sepal_ui.svg?branch=master)](https://travis-ci.com/12rambau/sepal_ui)
[![Maintainability](https://api.codeclimate.com/v1/badges/861f09002bb9d75b6ea5/maintainability)](https://codeclimate.com/github/12rambau/sepal_ui/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/861f09002bb9d75b6ea5/test_coverage)](https://codeclimate.com/github/12rambau/sepal_ui/test_coverage)

wrapper for ipyvuetify widgets to unify the display of voila dashboards in the sepal plateform.

![full_app](./doc/img/full_app.png)


## Installation 

the framework is available on Pypi:
```
$ pip install sepal_ui
```

The usage of this framework require that the earthengine api and it's authentification. Run:
```
$ earthengine authenticate
```
and follow the instructions

## Usage 

Click on the links to discover the different usage of the framework :
- Create an aoi selector [doc](./doc/aoi.md)
- Create an about section [doc](.doc.about.md)
- Link you process to a tile [doc](./doc/process.md)
- Create app framework with a title, a footer and a drawer menu [doc](./doc/app.md)


An example of app using this framwork can be found [here](https://github.com/12rambau/sepal_ui_template).

## suggested structure 

To use this framework it is highly recommanded to follow the following folder scructure:
```bash
├── app
│   ├── doc
│   │   ├── img
│   │   │   └── *.png 
│   │   │
│   │   └── *.md
│   │   
│   ├── scripts
│   │   └── you app process (*.py, *.cpp, *.r)
│   │
│   ├── [tile_name]_UI.ipynb
│   ├── UI.ipynb
│   │
│   └── ReadME.md
```

The `UI.ipynb` will be the entry point of you're app and it will call all the differents tiles created in the `[tile_name].ipynb` files.


For more specific and customized app. you can directly create your own component using the [ipyvuetify lib](https://github.com/mariobuikhuizen/ipyvuetify).

## Contribute 

If you want to contribute you can fork the project in you own repository and then use it. Please follow the [contributing guidelines](./CONTRIBUTE.md) if you consider working with us. 

To validate you modification go to the root folder of the package and run 
```py
python3 setup.py sdist
```

and install instead the one from your local folder 
```py
pip install [your_sepal_ui_folder]
```

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center">
      <a href="https://www.linkedin.com/in/pierrickrambaud/">
        <img src="https://avatars3.githubusercontent.com/u/12596392?v=4" width="70px;" alt="12rambau"/><br />
        <sub><b>Pierrick Rambaud</b></sub>
      </a><br />
      <a href="#code" title="Code">💻</a> 
      <a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a> 
      <a href="#question" title="Answering Questions">💬</a> 
      <a href="#issue" title="Bug reports">🐛</a> 
      <a href="#documentation" title="Documentation">📖</a> 
      <a href="#maintenance" title="Maintenance">🚧</a> 
      <a href="#review" title="Reviewed Pull Requests">👀</a> 
      <a href="#test" title="Tests">⚠️</a>
    </td>
    <td align="center">
      <a href="https://www.linkedin.com/in/danielguerrerosig/">
        <img src="https://avatars0.githubusercontent.com/u/12363250?s=400&v=4" width="70px;" alt="ingdanielguerrero"/><br />
        <sub><b>Daniel Guerrero</b></sub>
      </a><br />
      <a href="#code" title="Code">💻</a> 
      <a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a> 
      <a href="#question" title="Answering Questions">💬</a>  
      <a href="#documentation" title="Documentation">📖</a> 
      <a href="#example" title="Examples">💡</a>
      <a href="#review" title="Reviewed Pull Requests">👀</a> 
    </td>	
  </tr>
</table>

This project follows the [all-contributors](https://allcontributors.org) specification.
Contributions of any kind are welcome!
