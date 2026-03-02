"""A demo tile showing some of the most frequent widgets available in the sepal_ui library."""

import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.mapping.sepal_map import SepalMap


class WidgetTile(sw.Card):
    def __init__(self):
        """A demo tile showing all the widgets available in the sepal_ui library."""
        # create the card
        super().__init__(row=True, wrap=True, _metadata={"mount_id": "widget_tile"})

        # Create widgets

        select = sw.Select(
            label="Select",
            v_model="option1",
            items=["option1", "option2", "option3"],
            outlined=True,
        )

        slider = sw.Slider(
            label="Slider",
            v_model=50,
            max=100,
            min=0,
            thumb_label=True,
            step=1,
        )

        btn = sw.Btn("Button", color="primary", outlined=True)
        btn1 = sw.Btn("Button", color="secondary", outlined=True)
        btn2 = sw.Btn("Button", color="primary")
        btn3 = sw.Btn("Button", color="secondary")
        file_input = sw.FileInput()
        map_ = SepalMap(zoom=10)

        title = v.CardTitle(children=["test widgets tile"])

        card = v.Card(class_="mb-4 pa-2", raised=True, xs12=True, children=[title, map_])

        loading_card = v.Card(
            class_="mb-6 pa-2",
            raised=True,
            xs12=True,
            children=[title] + ["content " * 100],
            loading=True,
        )

        warning_alert = sw.Alert().add_msg("This is a warning alert", type_="warning")
        error_alert = sw.Alert().add_msg("This is an error alert", type_="error")
        info_alert = sw.Alert().add_msg("This is an info alert", type_="info")
        success_alert = sw.Alert().add_msg("This is a success alert", type_="success")

        # Add widgets to the layout

        self.children = [
            card,
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[select]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[file_input]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[slider]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[btn]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[btn1]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[btn2]),
            v.Flex(class_="mb-2", xs12=True, lg6=True, xl4=True, children=[btn3]),
            v.Flex(
                class_="mb-2",
                xs12=True,
                lg6=True,
                xl4=True,
                children=[warning_alert],
            ),
            v.Flex(
                class_="mb-2",
                xs12=True,
                lg6=True,
                xl4=True,
                children=[error_alert],
            ),
            v.Flex(
                class_="mb-2",
                xs12=True,
                lg6=True,
                xl4=True,
                children=[info_alert],
            ),
            v.Flex(
                class_="mb-2",
                xs12=True,
                lg6=True,
                xl4=True,
                children=[success_alert],
            ),
            loading_card,
        ]
