## v_2.11.0 (2022-09-01)

### Feat

- creates an overflow scrollbar when there is more than one subscription card
- add Sepal Map method to create and set legend
- hide legend when there is not content
- integrate levels of nicfi contract inside planet_view and planet_model
- add legend key to message box
- add Sepal Map method to create and set legend

### Refactor

- simplify structure
- support 'others' subscriptions
- small changes
- make optional model and trait, the object change method can be autonomously called
- upgrade planetapi object to match with planet>=2
- move to planet V2
- use message key for legend title

### Fix

- set all the links inlines
- FAO dark logo
- the logo is was wrong
- fix the json file
- transform legend into a legendControl
- #579
- fix imports error
- find forbiden keys recursivesly
- find forbiden keys recursivesly

## v_2.10.3 (2022-08-10)

### Fix

- lazy import localtileserver
- avoid reloading root when fileinput is already none

### Refactor

- .. spelling:word-list::
- reset method
- remove legacy print

## v_2.10.2 (2022-07-28)

### Fix

- use appropiate error
- lazy import of localtileserver

## v_2.10.1 (2022-07-25)

### Fix

- fix: add support for matplotlib cmap following advices from https://github.com/banesullivan/localtileserver/issues/103
- typo
- change raster detection
- drop usage of xarray-leaflet
- use class name
- close the controls when another one is opened Fix #551
- show alert when progess updates Fix #556
- set the navbar at the same z-index as map Fix #548
- remove toggle_button from map app Fix #549

### Refactor

- the alert is now fully compatible with tqdm
- the alert is now fully compatible with tqdm

## v_2.10.0 (2022-07-21)

### Refactor

- cleaning
- move decorator to their own modules
- move decorator to their own module
- isort the lib files
- remove matplotlib import
- edit style file structure
- change statebar behavior
- use json to store styling informations
- move check_input to utils
- use css and js file
- move check_input to utils Fix #513
- use noqa Fix #511
- deprecate zip_dir fix #514
- clean leftover + use tqdm.notebook
- use the new DrawControl to manage edited features
- aoi module

### Fix

- add the panel aaplication template
- add the map_app template
- add templates to the distibution
- update modul_factory
- stipout the notebooks
- trick to make sepal_ui work with Python 3.10
- use MenuControl in AoiControl
- use menucontrol with value inspector
- missing endif
- use a pattern in glob
- offset for the top navbar
- automatically nest tiles in menucontrol
- make the positioning optional
- add ipynb files to translator test
- use txt in mapbtn
- solve conflict with AoiControl
- be more specific in str testing
- lat/lng were inverted in haversine
- typo
- use relative path in tests
- remove existing unused keys
- solve all the issue created by moving color from style to init
- GeoJSON don't have loading member
- merge current master
- use 1single argument
- make the fulsscreen responsive to init status
- point to the correct variables in the translator Fix #521
- use txt in mapbtn Fix #510
- nest the card instead of the tile Fix #512
- remove unwanted notebooks
- describe the bug in the comment
- avoid mutate dc.data jsons. Identify circle geometries by type
- use search-location instead of at
- AppBar is not looking for the good one
- froze the Box to make sure it's never modified
- use box for encapsulated dict
- change color of the progress bar in alerts
- avoid bug on repeated click
- the points and vector were not triggering the v_model change event
- hide asset
- prevent crash when gee is set to false
- avoid 3.10 to be transformed in 3.1
- update translation keys
- hide the statebar on map build
- add the map loading state

### Feat

- add templates
- make it possible to change the menu size constraints
- add a menucontrol component
- first implementation of key_use
- open in fullscreen
- introduce tqdm progress bar. related with #294
- query only locales forlders
- add methods to deal with editions in DrawControl
- introduce tqdm progress bar. related with #294
- create an AoiControl widget

## v_2.9.4 (2022-06-09)

### Fix

- drop jupyter-sphinx git version I think the rendering is going to fail but it's preventing me from building the wheel and to use Jupyterlite I need the wheel Sorry not sorry

## v_2.9.3 (2022-06-09)

### Fix

- build the wheel

## v_2.9.2 (2022-06-09)

### Fix

- build the wheel

## v_2.9.1 (2022-06-09)

### Fix

- allow the build off the wheel

## v_2.9.0 (2022-06-09)

### Feat

- extend color simplenamspace to interactively display colors in …
- extend color simplenamspace to interactively display colors in jypyter
- refresh tooltip if there are new kwargs
- return basemap box as default object from basemaps module
- make wheel scroll default param
- add a MapBtn
- create planet handler
- add keys and fix review
- reset input fields when changing method
- capture any other errors, direcrtyl from api
- introduce StateIcon. An interactive icon.
- make alert and button optional elements
- create stand alone Planet credentials view
- create planet handler

### Refactor

- adapt tests to get the current theme"
- enrich color object to display both theme colors
- deprecate specific set theme and create generic function
- initialize configuration file and make it available to all modules
- improve zoom_bounds quality
- improve zoom_ee_object quality
- instantiate config parser and import in init
- deprecate is_absolute
- deprecate is_absolute
- overwrite default sw default Tooltip object
- rename tooltip wrapper widget
- remove uncalled skips
- set viz parameter outside of kwargs
- use keys for vinspector messages
- rename value inspector module and add a closing icon
- some line breaks and removed a pair of condionals
- reorder the coordinates
- move the v_inspector away from SepalMap
- cleaning
- split the gee command override from the rest of SepalMap
- use sepalwidgets StateIcon component
- admit any type for value trait
- add kwargs to the StateIcon
- make command cli tools as python scripts to align autoprogram plugin
- make parser var name descriptive and add module commands to path
- use a fake init key
- undo test
- remove dust
- raise error when credentials empty
- move theDrawControl to its own file It will be supporting the drawing methods (editing, polygonize) from there
- clean the import of ipyleaflet widgets
- add translation keys for navdrawer items
- add translation keys for navdrawer items
- rename files
- rename planet to avoid main planet package ambibuity

### Fix

- zoom automatically on raster layers
- digest all ee.ComputedObject
- legacy assert
- fullscreen control now specify which map to fullscreen
- add the none_ok parameter to find_layer
- remove bind method from Alert
- skip planet test if no API key
- remove bind method from Alert Fix #295
- skip planet test if no API key Fix #481
- add_tooltip method
- typo
- include a base filter to sepal_map search and delete methods
- prepare refactoring of ValueInspector
- avoid the v_inspector to move down the map
- remove legacy dot on the map Fix #456
- inspect rasters
- read GeoJSON data
- inspect ee_objects
- remove background for btns on maps
- closes #466
- doc typo
- typo
- closes #466
- validate when there is no initial value in module
- add missing import
- use quotes to define the planet_credentials
- remove empty string from the translation dict
- use keys for the fileinput placeholder Fix #464
- avoid circular reference
- geemap was still called in aoi_model
- remove_all method to remove all layers but the basemaps
- overwrite remove_layer to use index, name or layer
- find layer by name and by index
- set the basemaps as basemaps #422
- drop usage of geemap + cleaning #455
- continue using geemap 0.8.9
- remove empty string from the translation dict Fix #449
- fix #452

## v_2.8.0 (2022-04-18)

### Fix

- remove empty versions from the changelog
- prevent Alert with no parameters to raise a warning
- backward compatibility of the type parameter
- use msg for banner btn
- only display the oldest banner queue the other and hide them
- raise a warning if type is badly defined
- display the number of stackbar in the queue
- create the disclaimer tile on the fly
- change logo source in light theme
- unproject images in add_raster
- unproject images in add_raster Fix #434

### Feat

- new set and get children to sepalwidget. Aims to close #443
- create Banner widget to display important message to end-user
- override ipyleaflet Map  add_layer method to use default style

### Refactor

- rename _tmp class name with the actual new sepalwidget name
- deal with type_ the same way we do it in Alert
- use a persistent parameter instead of timeout
- simplify add_banner method by calling Banner widget
- return map when new layer added + make more clear param name
- change alert by snackbar when creating a banner aims to close #438
- move theme, color and theme function to styles

## v_2.7.0 (2022-03-28)

### Refactor

- get folder name instead stem
- change kernel by venv. reset df index
- clean leftover
- don't use shell=True
- reduce line number
- sanityse scripts
- cleaning
- use observe decorator
- observe alert trait even though no model

### Feat

- cmd script to activate virtual envs
- warn user this process will take some time
- avoid adding multiple banners
- control the theme using a btn
- add theme in the config file
- add interaction with drawer. closes #415
- new fullscreen widget
- new LocaleSelect widget
- function to update config language
- allow the tranlator to read config file
- new fullscreen widget

### Fix

- use repository name instead of stem
- guess the languages available
- check that the folder is a module directory
- add a script to test enviroment
- remove alert if change of the same parameter
- set return statement
- trigger the icon change
- display only one alert per type use a lambda function and next intead of multiple ifs. set the v_model to false to systematically see the transition
- specify the archive format
- solve build issue in RDT
- typo in attribution map
- the lib translator was still using the old implementation
- display message to the end user when changing theme
- change menus colors according to theme
- control selected aoi color
- adapt map basemap to theme
- control the theming with the config file
- control datepicker value using v_model
- us all .json in l10n folders
- create a script to switch language parameters from terminal
- display only the locales available for the current app
- display only the locales available for the current app
- use mdi icons in Numberfields
- password eyes not diplayed
- use mdi icons for pre-designed prepend-icon Fix #414
- display messages to the end user on locale change
- make the localSelector responsive to translator values
- add the Local widget in the navbar
- change config file on click
- debug non working flags
- support for subvarieties of language Fix #408
- add a disabled trait to datepicker Fix #409

## v_2.6.2 (2022-02-18)

### Fix

- prevent crash when badly design viz params are used Fix #405

## v_2.6.1 (2022-02-17)

### Fix

- add the message file in the distrib
- make readme copatible with pypi release
- make readme compatible with pypi release  has syntax errors in markup and would not be rendered on PyPI.     line 6: Error: Document or section may not begin with a transition.

## v_2.6.0 (2022-02-16)

### Refactor

- ignore untitled files
- ignore untitled files
- remove __setattr__ magic method.
- typo in class name
- remove __setattr__ magic method.
- reshape messages to fit the translator requirements
- replace every occurence of mdi icons
- use `/` in Path

### Fix

- remove fr file from merge
- avoid deprecation by reshaping dictionnary
- remove {locale}.json files
- remove list from json files potoon is not compatible with lists but only key dictionaries
- add basepath
- set the name in the properties of the GEJSON output
- don't use the named 'tmp' directory
- don't use the named 'tmp' directory Fix #391
- set the name in the properties of the GEJSON output Fix #390
- typo

### Feat

- change translator behaviour to meet l10n requirements

## v_2.5.5 (2022-01-12)

### Fix

- avoid meta sepal when clicking on download btn

## v_2.5.4 (2022-01-11)

### Fix

- scroll back to the top when change folde Fix #232
- only install pre-commit hooks once
- only install pre-commit hooks once Fix #373
- use https instead of git
- reset model output when selecting a new AOI Fix #366

### Refactor

- cleaning

## v_2.5.3 (2021-12-08)

### Fix

- solve the build issue in SEPAL
- cryptography since flake8 linting cryptography is not a lazy dependency anymore
- install missing packages

## v_2.5.2 (2021-12-07)

### Fix

- prevent bug when image have no properties Fix #361

## v_2.5.1 (2021-12-07)

### Fix

- git based libs are not compatible with pipy

## v_2.5.0 (2021-12-06)

### Refactor

- use named arguments to improve readability
- import sepal_ui after sys
- use flake8 in pre-commit
- reset github folder as hidden
- remove deprecation notice
- minor logical operator writing
- deprecate toggle
- use class management methods Fix #119
- use kwargs pop
- fix some of the parameters
- remove __init__ in model
- use kwargs pop Avoid the duplication of parameter using an elegant and python method called dict poping
- add black basge Fix #326
- black typo
- remove legacy print
- typo in package name
- change lib name Change the lib name to meet the name used in PiPy Some change will need to be done in the documentation to reflect this change
- use * instead of list comprehension

### Fix

- manage inverted bands
- display hsv images
- display categorical values without sld
- specific case of hsv display
- specific case of categorical data
- handle when the viz_name is not in the image
- overwrite addLayer to read metadata display parameters
- add the colors to the documentation Fix #312
- display folder as folder even when there is a suffix Fix #350
- display vrt file as images Fix #351
- change internal structure of widgets Improve coverage by testing markdown
- Sepalwidget set viz
- close fileinput menu when v_model is set
- close menu when date is selected Fix #17
- viz can be set in params
- make viz into a trait It now controls the vizibility
- hide the icon if set to empty
- set back the missing members
- hide the icon is set to empty
- add increm parameter
- change param
- reload assetSelect on types change Fix #323
- prevent setting asset of wrong type Fix #322
- limit the items list to type The self.items += is not a usable operator for list trait I was force to use a tmp list to really update the filter the items
- typo in Réunion name
- open link in new tabs Fix #311
- adapt test to new libs
- add a banner on top of app Fix #314
- init the items of the ClassTable Fix #313

### Feat

- overwrite all vuetify components
- overwrite all vuetify components

## v_2.4.0 (2021-10-19)

### Feat

- filter by column and value in AOI.
- filter by column and value in AOI. - closes: #296

### Fix

- display specific warnings in alerts
- replace default v_model fon VectorField as trait
- doc build failed
- only display SepalWarning in Alerts
- this assignation was overwritting the w_asset dict
- vector field method. closes #306

### Refactor

- make v_model default and empty value as None instead of empty string
- be consistent when concatenating

## v_2.3.0 (2021-10-06)

### Fix

- add enforce_aoi to reclassify_model
- use split instead of indexing Fix #302
- prevent tooltip error when calling. closes #298
- prevent tooltip error when calling. closes #298
- little typo
- fiix some minor bugs and add human sorted

### Refactor

- create destination gee unique name before export
- move exceptions from view to model
- remove _chk_dst_file method, its process was duplicated in the _set_dst_class file method

### Feat

- new script to Create a string followed by a consecutive underscore and number
- test reclassify model coverage=80%
- create useful fixtures to implement in related tests.
- create a tests rasters to test reclassify methods

## v_2.2.1 (2021-09-30)

### Fix

- typo in version naming

## v_2.2.0 (2021-09-30)

### Fix

- use ssh url in module_factory Fix #283
- typo
- clip margins
- use RPC to serve the resize method
- use RPC to serve the resize method
- catch when on_widget and targets have different length
- get the widget instead of the widget name
- local variable referenced before assignment
- **docs**: fix typo
- include the save parameter to the view when someones initialize the view without the model

### Refactor

- remove un-used method
- renamed Clip -> CopyToClip
- only set targets at the begining
- create a state bar to control if a table is already created
- use switch decorator
- make all view children elements part of the View class

### Feat

- declare all variable
- Copy to clipboard
- add copy-to-clipboard widget
- create common used fixtures
- add a targets parameter to switch method
- test reclassify model
- add a target parameter in the switch method
- create validation for the reclassify model method

## v_2.1.1 (2021-09-15)

### Fix

- typo in setup

## v_2.1.0 (2021-09-15)

### Fix

- folder init in reclassifyTile
- typo in json dict
- display the btn at the bottom of the table
- display a message to the user when reclassify
- default to 0 if class is not specified
- use the SEPAL coloring parameters
- use the folder name
- small UI bug
- use init_ee instead of ee.initialize()
- import table
- minor typo
- remove type and feat: introducing switch decorator
- remove type

### Refactor

- **lang**: add keys
- remove test notebook
- ensure a value is set to the func
- only set w_image to the appropriate widget
- add new keys in translation
- remove ununsed break
- fix merge conflict
- only init ee if needed
- remove usage of gee in documentation
- remove unused file
- change the image visualization function (black-formatter).
- extend the behavior of switch decorator with the last comments. closes #263
- adapt table view widget to the parameter SCHEME. Remove ambiguity when handling widgets values by adding _metadata attribute
- move SCHEMA variable from translation key to parameters to avoid ambiguity
- drop pre-commit autoupdate
- typo
- reintroduce type attribute
- fix french typos
- create __all__ variable to fix imports
- place __all__ at the file start

### Feat

- change state when something is loaded
- test asset validity
- add commitizen check
- improve sanity checks
- separate the reclassified image and its visualization
- define default_asset trait in SelectAsset. it will accept whether strings for unique default assets or lists for multiple. The trait can be observed to update the list anytime
- introducing switch decorator
- improve assetSelect component
