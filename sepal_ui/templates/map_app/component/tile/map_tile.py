from ipyleaflet import WidgetControl
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


class MapTile(sw.Tile):
    def __init__(self):

        # create a map
        self.m = sm.SepalMap(zoom=3)  # to be visible on 4k screens
        self.m.add_control(
            sm.FullScreenControl(
                self.m, fullscreen=True, fullapp=True, position="topright"
            )
        )

        # create the tile
        super().__init__("map_tile", "", [self.m])

    def set_code(self, link):
        "add the code link btn to the map"

        btn = sm.MapBtn("fas fa-code", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add_control(control)

        return

    def set_wiki(self, link):
        "add the wiki link btn to the map"

        btn = sm.MapBtn("fas fa-book-open", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add_control(control)

        return

    def set_issue(self, link):
        "add the code link btn to the map"

        btn = sm.MapBtn("fas fa-bug", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.m.add_control(control)

        return
