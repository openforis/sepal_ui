# Create an app framwork

Using this framework, you'll be able to build an app framework using Ipyvuetify components pre-selected for the sepal environment. 

# code 

```py
from sepal_ui import widgetFactory as wf
from sepal_ui import widgetBinding as wb

#create an appBar 
fao_appBar, fao_toggleButton = wf.AppBar('My fake module')

#create a footer 
fao_footer = wf.Footer('The sky is the limit \u00A9 2020')

#add your tiles
%run 'aoi_UI.ipynb'
%run 'process_UI.ipynb'
%run 'about_UI.ipynb'

fao_content = [fao_aoi, fao_process, fao_results, fao_about] #use the name created in the other .ipynb files

#select the tile to display first 
select = 'process_widget' #id of the tile you want to display
wf.hideCards(select, fao_content)

#create a drawer 
item_aoi = wf.DrawerItem('AOI selection', 'mdi-map-marker-check', card="aoi_widget")
item_tile = wf.DrawerItem('Process', 'mdi-cogs', card="process_widget")
item_result = wf.DrawerItem('Results', 'mdi-chart-bar', card="result_widget")
item_about = wf.DrawerItem('About', 'mdi-help-circle', card="about_widget")

code_link = 'https://github.com/12rambau/sepal_ui_template'
wiki_link = 'https://github.com/12rambau/sepal_ui_template/blob/master/doc/fake_doc.md'
issue = 'https://github.com/12rambau/sepal_ui_template/issues/new'

items = [item_aoi, item_tile, item_result, item_about]
fao_drawer = wf.NavDrawer(items, code = code_link, wiki = wiki_link, issue = issue)

#build the app 
fao_app = wf.App(
    tiles=fao_content, 
    appBar=fao_appBar, 
    footer=fao_footer, 
    navDrawer=fao_drawer
)[0]

#bind the components together
wb.displayDrawer(fao_drawer, fao_toggleButton) #drawer 
for item in items:                             #drawer clickable buttons
    wb.display_tile(item, fao_content)

#display the app
fao_app
```