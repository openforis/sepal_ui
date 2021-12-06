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
- fix some of the parameters
- remove __init__ in model
- use kwargs pop Avoid the duplication of parameter using an elegant and python method called dict poping
- add black basge Fix #326
- black typo
- remove legacy print
- typo in package name
- change lib name Change the lib name to meet the name used in PiPy Some change will need to be done in the documentation to reflect this change
- use * instead of list comprehension
- make v_model default and empty value as None instead of empty string
- be consistent when concatenating

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
- set back the missing members
- hide the icon is set to empty
- add increm parameter
- change param
- reload assetSelect on types change Fix #323
- prevent setting asset of wrong type Fix #322
- limit the items list to type The self.items += is not a usable operator for list trait I was force to use a tmp list to really update the filter the items
- typo in Réunion name
- open link in new tabs Fix #311
- add a banner on top of app Fix #314
- init the items of the ClassTable Fix #313
- replace default v_model fon VectorField as trait
- doc build failed
- only display SepalWarning in Alerts
- this assignation was overwritting the w_asset dict
- vector field method. closes #306

### Feat

- overwrite all vuetify components
- overwrite all vuetify components
- filter by column and value in AOI. - closes: #296

## v_2.3.0 (2021-10-06)

### Fix

- add enforce_aoi to reclassify_model
- use split instead of indexing Fix #302
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
- catch when on_widget and targets have different length
- get the widget instead of the widget name
- local variable referenced before assignment
- **docs**: fix typo
- include the save parameter to the view when someones initialize the view without the model
- typo in setup
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
- remove type

### Refactor

- remove un-used method
- renamed Clip -> CopyToClip
- only set targets at the begining
- create a state bar to control if a table is already created
- use switch decorator
- make all view children elements part of the View class
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
- place __all__ at the file start

### Feat

- declare all variable
- add copy-to-clipboard widget
- create common used fixtures
- test reclassify model
- add a target parameter in the switch method
- create validation for the reclassify model method
- change state when something is loaded
- test asset validity
- add commitizen check
- improve sanity checks
- separate the reclassified image and its visualization
- define default_asset trait in SelectAsset. it will accept whether strings for unique default assets or lists for multiple. The trait can be observed to update the list anytime
- introducing switch decorator

## v_2.0.3 (2021-06-09)

## v_2.0.2 (2021-06-08)

## v_2.0.1 (2021-06-02)

## v_2.0.0 (2021-05-26)

## v_1.1.5 (2021-04-02)

## v_1.1.4 (2021-03-26)

## v_1.1.3 (2021-03-26)

## v_1.1.2 (2021-03-24)

## v_1.1.1 (2021-03-17)

## v_1.1.0 (2021-02-26)

## v_1.0.2 (2021-01-15)

## v_1.0.1 (2020-12-24)

## v_1.0.0 (2020-12-04)

## v_0.7.9 (2020-11-19)

## v_0.7.8 (2020-11-16)

## v_0.7.7 (2020-11-05)

## v_0.7.6 (2020-11-02)

## v_0.7.5 (2020-11-02)

## v_0.7.4 (2020-11-02)

## v_0.7.3-beta (2020-10-09)

## v_0.7.2-beta (2020-10-09)

## v_0.7.1-beta (2020-09-18)

## v_0.7-beta (2020-09-17)

## v_0.6-beta (2020-09-14)

## v_0.5-beta (2020-08-11)

## v_0.4-beta (2020-08-06)

## v_0.3-beta (2020-07-31)

## v_0.2-beta (2020-07-27)

## v_0.1.11-alpha (2020-07-27)

## v_0.1.10-alpha (2020-07-27)

## v_0.1.9-alpha (2020-07-27)

## v0.1.8-alpha (2020-07-27)

## v_0.1.7-alpha (2020-07-27)

## v_0.1.6-alpha (2020-07-27)

## v_0.1.5-alpha (2020-07-27)

## v_0.1.4-alpha (2020-07-27)

## v_0.1.3-alpha (2020-07-27)

## v_0.1.2-alpha (2020-07-27)

## v_0.1-alpha (2020-07-27)

## v_0.0-alpha (2020-07-27)