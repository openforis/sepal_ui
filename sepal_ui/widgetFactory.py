from markdown import markdown
from datetime import datetime
import traitlets
import os

import ipyvuetify as v

from sepal_ui import widgetBinding as wb
from sepal_ui.scripts import mapping, utils


sepal_main = '#2e7d32'
sepal_darker = '#005005'

#create a app bar 
def AppBar(title='SEPAL module'):
    """
    create an appBar widget with the provided title using the sepal color framework
    
    Returns: 
        app (v.AppBar) : The created appbar
        toolbarButton (v.Btn) : The button to display the side drawer
    """

    toolBarButton = v.Btn(
        icon = True, 
        children=[
            v.Icon(class_="white--text", children=['mdi-dots-vertical'])
        ]
    )
    
    appBar = v.AppBar(
        color=sepal_main,
        class_="white--text",
        dense=True,
        app = True,
        children = [
            toolBarButton, 
            v.ToolbarTitle(children=[title]),
        ]
    )
    
    return (appBar, toolBarButton)
    
#create a drawer_item
def DrawerItem(title, icon=None, card='', href=''):
    """ 
    create a drawer item using the user input
    
    Args:
        title (str): the title to display in the drawer,
        icon (str, optional): the icon id following the mdi code. folder icon if None
        card (str), optional): the tile metadata linked to the drawer
        href(str, optional): the link targeted by the button
    
    Returns:
        item (v.ListItem): the item to display
    """
    
    if not icon:
        icon = 'mdi-folder-outline'
        
    item = v.ListItem(
        link=True,
        children=[
            v.ListItemAction(
                children=[
                    v.Icon(
                        class_="white--text", 
                        children=[icon])
                ]
            ),
            v.ListItemContent(
                children=[
                    v.ListItemTitle(
                        class_="white--text", 
                        children=[title]
                    )
                ]
            )
        ]
    )
    
    if not href == '':
        item.href=href
        item.target="_blank"

    if not card == '':
        item._metadata = {'card_id': card }
    
    return item

#create a drawer 
def NavDrawer(items, code = False, wiki = False, issue = None):
    """ 
    create a navdrawer using the different items of the user and the sepal color framework. The drawer always include links to the github page of the project for wiki, bugs and repository.
    
    Args:
        items ([v.ListItem]) : the list of the list item the user wants to add to the nav drawer
        code (str, optionnal) : the absolute link to the github code. not display if None
        wiki (str, optionnal) : the absolute link to the github wiki. not display if None
        issue (str, optionnal) : the absolute link to the github issues. not display if None
    
    Returns:
        navDrawer (v.NavigationDrawer) : the nav drawer of the web page
    """
    
    code_link = []
    if code:
        item_code = DrawerItem('Source code', icon='mdi-file-code', href=code)
        code_link.append(item_code)
    if wiki:
        item_wiki = DrawerItem('Wiki', icon='mdi-book-open-page-variant', href=wiki)
        code_link.append(item_wiki)
    if issue:
        item_bug = DrawerItem('Bug report', icon='mdi-bug', href=issue)
        code_link.append(item_bug)
        
    
        
    navDrawer = v.NavigationDrawer(
        v_model=True, 
        app= True,
        color=sepal_darker,
        children=[
            v.List(dense=True, children=items),
            v.Divider(),
            v.List(dense=True, children=code_link),
        ]
    )
    
    return navDrawer


#create a footer 
def Footer (text='SEPAL \u00A9 2020'): 
    """ 
    create a footer with cuzomizable text. Not yet capable of displaying logos
    
    Returns: 
        footer (v.Footer) : an app footer
    """
    
    footer = v.Footer(
        color=sepal_main,
        class_="white--text",
        app = True,
        children = [text]
    )
    
    return footer


#create an app
def App (tiles=[''], appBar=None, footer=None, navDrawer=None):
    """
    Create an app display with the tiles created by the user. Display false footer and appBar if not filled. navdrawer is fully optionnal
    
    Args:
        tiles ([v.Layout]) : the list of tiles the user want to display in step order. 
        appBar (v.appBar, optionnal) : the custom appBar of the module
        footer (v.Footer, optionnal) : the custom footer of the module
        navDrawer (v.NavigationDrawer, optional) : the navigation drawer to allow the display of specific tiles
        
    Returns:
        app (v.App) : the complete app to display
        toolBarButton (v.Btn) : the created toolbarButton, None if the appBar was already existing
    """
    
    app = v.App(v_model=None)
    app_children = []
    
    #add the navDrawer if existing
    if navDrawer:
        app_children.append(navDrawer)
    
    #create a false appBar if necessary
    toolBarButton = None
    if not appBar:
        appBar, toolBarButton = AppBar()
    app_children.append(appBar)

    #add the content of the app
    content = v.Content(children=[v.Container(fluid=True,children = tiles)])
    app_children.append(content)
    
    #create a false footer if necessary
    if not footer:
        footer = Footer()
    app_children.append(footer)

    app.children = app_children
    
    return (app, toolBarButton)

#create a tile 
def Tile(id_, title, inputs=[''], btn=None, output=None):
    """ 
    create a customizable tile for the sepal UI framework
    
    Args: 
        id_ (str) : the Id you want to gave to the tile. This Id will be used by the draweritems to show and hide the tile.
        title (str) : the title that will be display on the top of the tile
        btn (v.Btn, optionnal) : if the tile launch a py process, attached a btn to it.
        output( v.Alert, optional) : if you want to display text results of your process add an alert widget to it
        
    Returns: 
        tile (v.Layout) : a fully functionnal tile to be display in an app
    """
    
    if btn:
        inputs.append(btn)
    
    if output:
        inputs.append(output)
        
    
    inputs_widget = v.Layout(
        _metadata={'mount-id': '{}-data-input'.format(id_)},
        row=True,
        class_="pa-5",
        align_center=True, 
        children=[v.Flex(xs12=True, children=[widget]) for widget in inputs]
    )
    
    tile = v.Layout(
        _metadata={'mount_id': id_},
        row=True,
        xs12=True,
        align_center=True, 
        class_="ma-5 d-inline",
        children=[
            v.Card( 
                class_="pa-5",
                raised=True,
                xs12=True,
                children=[
                    v.Html(xs12=True, tag='h2', children=[title]),
                    v.Flex(xs12=True, children=[inputs_widget]),   
                ]
            )
        ]
    )
    
    return tile

#create the about tile 
def TileAbout(pathname):
    """
    create a about tile using a md file. This tile will have the "about_widget" id and "About" title.
    
    Args:
        pathname (str) : the pathname to the .md file of the about section
        
    Returns:
        tile (v.Layout) : a about tile
    """
    
    #read the content and transform it into a html
    f = open(pathname, 'r')
    if f.mode == 'r':
        about = f.read()
    else :
        about = '**No About File**'
        
    about = markdown(about, extensions=['fenced_code', 'sane_lists'])
    
    #need to be nested in a div to be displayed
    about = '<div>\n' + about + '\n</div>'
    
    #create a Html widget
    class MyHTML(v.VuetifyTemplate):
        template = traitlets.Unicode(about).tag(sync=True)
    
    
    content = MyHTML()
    
    #content = w.HTML(value=about)
    
    return Tile('about_widget', 'About', inputs=[content])

#create the disclaimer tile 
def TileDisclaimer():
    """
    create a about tile using a md file. This tile will have the "about_widget" id and "Disclaimer" title. It will be display at the same time as the about section
        
    Returns:
        tile (v.Layout) : a about tile
    """
    
    pathname = os.path.join(os.path.dirname(__file__), 'scripts', 'disclaimer.md')
    
    #read the content and transform it into a html
    f = open(pathname, 'r')
    if f.mode == 'r':
        about = f.read()
    else :
        about = '**No Disclaimer File**'
        
    about = markdown(about, extensions=['fenced_code', 'sane_lists'])
    
    #need to be nested in a div to be displayed
    about = '<div>\n' + about + '\n</div>'
    
    #create a Html widget
    class MyHTML(v.VuetifyTemplate):
        template = traitlets.Unicode(about).tag(sync=True)
    
    
    content = MyHTML()
    
    #content = w.HTML(value=about)
    
    return Tile('about_widget', 'Disclaimer', inputs=[content])

#create downloadable links button 
def DownloadBtn(text, path="#"):
    """
    Create a green downloading button with the user text
    
    Args:
        text (str): the text to display in the downloading button
        path (str): the path to the asset, can be a relative path to your sepal folder or an absolute url
        
    Returns:
        btn (v.Btn) : the btn that will pop a new downloadable link
    """
    #create the url
    if utils.is_absolute(path):
        url = path
    else: 
        url = utils.create_download_link(path)
    
    btn = v.Btn(
        class_='ma-2',
        xs5=True,
        color='success',
        href=url,
        children=[
            v.Icon(left=True, children=['mdi-download']),
            text
        ]
    )
    
    return btn

#create a process button 
def ProcessBtn(text="Launch process"):
    """
    create a process button filled with the provided text
    
    Returns: 
        btn (v.Btn) : the btn
    """
    btn = v.Btn(
        color='primary', 
        children=[
            v.Icon(left=True, children=['mdi-map-marker-check']),
            text
        ]
    )
    
    return btn

#hide all the cards but one for the start of the notebook
def hideCards(tileId, tiles):
    """
    hide all the cards but the on selected
    
    Args: 
        tileId (str) : the card to be display when opening the app 
        tiles ([v.cards]) : a list of the cards in the app
    """
    for tile in tiles:
            if tileId == tile._metadata['mount_id']:
                tile.class_="ma-5 d-inline"
            else:
                tile.class_="ma-5 d-none"
    

#create the aoi selectors IO
class Aoi_IO:
    def __init__(self):
        #set up your inputs
        self.file_input = None
        self.file_name = 'Manual_{0}'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None
    
        #set up your output
        self.assetId = None

#create an aoi selector tile with all its bindings
def TileAOI(io):
    """render and bind all the variable to create an autonomous aoi selector. It will create a asset in you gee account with the name 'aoi_[aoi_name]'. The assetId will be added to io.assetId.
    
    Args: 
        io (Aoi_IO) : an Aoi_IO object that content all the IO of the aoi selector tile in your app
        
   Returns:
       tile (v.Layout) : an autonomous tile for AOI selection binded with io
   """
    
    #constants
    selection_method = [
        'Country boundaries', 
        'Draw a shape', 
        'Upload file', 
        'Use GEE asset'
    ]
    AOI_MESSAGE='Click on "Selet these inputs" to validate your AOI'
    
    #create the output
    aoi_output = OutputWidget(AOI_MESSAGE)
    
    #create the inputs widgets 
    aoi_file_input = v.Select(
        items=utils.get_shp_files(), 
        label='Select a file', 
        v_model=None,
        class_='d-none'
    )
    wb.bind(aoi_file_input, io, 'file_input', aoi_output)
    
    aoi_file_name = v.TextField(
        label='Select a filename', 
        v_model=io.file_name,
        class_='d-none'
    )
    wb.bind(aoi_file_name, io, 'file_name', aoi_output)
    
    aoi_country_selection = v.Select(
        items=[*utils.create_FIPS_dic()], 
        label='Country/Province', 
        v_model=None,
        class_='d-none'
    )
    wb.bind(aoi_country_selection, io, 'country_selection', aoi_output)
    
    aoi_asset_name = v.TextField(
        label='Select a GEE asset', 
        v_model=None,
        class_='d-none'
    )
    wb.bind(aoi_asset_name, io, 'assetId', aoi_output)
    
    widget_list = [aoi_file_input, aoi_file_name, aoi_country_selection, aoi_asset_name]
    
    #create the map 
    dc, m = mapping.init_map()
    wb.handle_draw(dc, io, 'drawn_feat', aoi_output)
    
    #bind the input to the selected method 
    aoi_select_method = v.Select(items=selection_method, label='AOI selection method', v_model=None)
    wb.bindAoiMethod(aoi_select_method, widget_list, io, m, dc, selection_method)
    

    #create the validation button 
    aoi_select_btn = ProcessBtn('Select these inputs')
    wb.bindAoiProcess(aoi_select_btn, io, m, dc, aoi_output, selection_method)
    
    #assemble everything on a tile 
    inputs = v.Layout(
        _metadata={'mount-id': 'data-input'},
        class_="pa-5",
        row=True,
        align_center=True, 
        children=[
            v.Flex(xs12=True, children=[aoi_select_method]),
            v.Flex(xs12=True, children=[aoi_country_selection]),
            v.Flex(xs12=True, children=[aoi_file_input]),
            v.Flex(xs12=True, children=[aoi_file_name]),
            v.Flex(xs12=True, children=[aoi_asset_name]),
            v.Flex(xs12=True, children=[aoi_select_btn]),
            v.Flex(xs12=True, children=[aoi_output]),
        ]
    )

    AOI_content_main =  v.Layout(
        _metadata={'mount_id': 'aoi_widget'},
        xs12=True,
        row=True,
        class_="ma-5 d-inline",
        children=[
            v.Card(
                class_="pa-5",
                raised=True,
                xs12=True,
                children=[
                    v.Html(xs12=True, tag='h2', children=['AOI selection']),
                    v.Layout(
                        row=True,
                        xs12=True,
                        children=[
                            v.Flex(xs12=True, md6=True, children=[inputs]),
                            v.Flex(class_="pa-5", xs12=True, md6=True, children=[m])
                        ]
                    )    
                ]
            )
        ]
    )
    
    return AOI_content_main

#create an alert 
def OutputWidget(text='Click it', type_='info'):
    """
    create an output alert that can be used to display the process outputs
    
    Args:
        text (str, optionnal): the text to display in the output
        type (str, optionnal): the initial color of the alert
    """
    list_color = ['info', 'success', 'warning', 'error']
    if not type_ in list_color:
        type_ = 'info'
        
    alert = v.Alert(children=[text], type=type_, text=True, class_="mt-5")
    
    return alert
    
    
    
