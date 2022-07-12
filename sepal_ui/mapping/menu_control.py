from ipyleaflet import WidgetControl

from sepal_ui import sepalwidgets as sw
from sepal_ui.mapping.map_btn import MapBtn


class MenuControl(WidgetControl):
    """
    Widget control displaying a btn on the map. When clicked the menu expand to show the content set by the user.
    It's used to display interactive tiles directly in the map. If the card_content is a Tile it will be automatically nested.

    Args:
        icon_content (str): the icon content as specified in the sm.MapBtn object (i.e. a 3 letter name or an icon name)
        card_content (container): any container from sw. The sw.Tile is specifically design to fit in this component
    """

    menu = None
    "sw.Menu: the menu displayed on the map as a widget"

    def __init__(self, icon_content, card_content, **kwargs):

        # create a clickable btn
        btn = MapBtn(content=icon_content, v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}

        # nest the content if it's a sw.Tile
        children = [card_content]
        if isinstance(card_content, sw.Tile):
            card_title = sw.CardTitle(children=[card_content.get_title()])
            children.append(card_title)
            card_content.nest()
            card_content.class_list.replace("ma-5", "ma-0")
            card_content.children[0].class_list.remove("pa-5")
            card_content.children[0].raised = False
            card_content.children[0].elevation = 0

        # set up the content style
        card = sw.Card(
            tile=True,
            max_height="40vh",
            min_height="40vh",
            max_width="400px",
            min_width="400px",
            style_="overflow: auto",
            children=children,
        )

        # assemble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[card],
            v_slots=[slot],
            offset_x=True,
        )

        # by default MenuControls will be displayed in the bottomright corner
        kwargs["position"] = kwargs.pop("position", "bottomright")
        kwargs["widget"] = self.menu

        super().__init__(**kwargs)

        # place te menu according to the widget positioning
        self.update_position(None)
        self.observe(self.update_position, "position")

    def update_position(self, change):
        """
        update the position of the menu if the position of the widget is dynamically changed
        """

        self.menu.top = "bottom" in self.position
        self.menu.bottom = "top" in self.position
        self.menu.left = "right" in self.position
        self.menu.right = "left" in self.position
        return
