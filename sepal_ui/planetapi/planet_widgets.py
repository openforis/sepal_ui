from datetime import datetime, timezone

import ipyvuetify as v

import sepal_ui.sepalwidgets as sw

btns = {
    "level_0": ["Level 0", ["menu", "success"]],
    "level_1": ["Level 1", ["menu", "success"]],
    "level_2": ["Level 2", ["menu", "success"]],
}


class InfoView(sw.ExpansionPanels):
    """
    Custom optinal card to be displayed within the planet view to validate the available
    subscriptions from the log-in credentials and show the info related with them, such
    as the quotas and remaining time of activation.

    """

    model = None
    "sepal_ui.planetapi.PlanetModel: backend model to manipulate interface actions"

    def __init__(self, model, *args, **kwargs):

        self.model = model
        self.v_model = 1
        self.current_level = None
        self.readonly = True

        super().__init__(*args, **kwargs)

        subs_btn = [
            sw.Chip(
                children=[btns[label][0]],
                disabled=True,
                color=btns[label][1][0],
                x_small=True,
                class_="mr-2",
                attributes={"id": label},
                link=True,
                label=True,
            )
            for label in ["level_0", "level_1", "level_2"]
        ]

        self.info_card = InfoCard().hide()

        self.children = [
            v.ExpansionPanel(
                children=[
                    v.ExpansionPanelHeader(children=[v.Flex(children=subs_btn)]),
                    v.ExpansionPanelContent(v_model=1, children=[self.info_card]),
                ]
            )
        ]

        [chip.on_event("click", self.open_info) for chip in subs_btn]

        self.model.observe(self._toggle_btns, "active")

    def open_info(self, widget, event, data):
        """Srhink or srhunk the content of the expansion panel, sending a request to
        build the data"""
        if self.current_level == widget.attributes["id"]:
            self.v_model = (not self.v_model) * 1
        else:
            self.v_model = 0

        self.current_level = widget.attributes["id"]

        subscription = self.model.subscriptions[self.current_level]

        self.info_card.update(subscription).show()

    def _toggle_btns(self, change):
        """Activate specific button. It will be available if the subscription
        to that level is active"""

        if change["new"] is False:
            self.v_model = 1

        for btn_id in btns.keys():
            btn = self.get_children(btn_id)
            btn.disabled = not change["new"]
            btn.color = btns[btn_id][1][change["new"]]


class InfoCard(sw.Card):
    """Information card that will display the subscription data"""

    def __init__(self):

        super().__init__()

        self.w_state = sw.StateIcon(
            states={
                "non_active": ["Non active", "error"],
                "active": ["Active", "success"],
            }
        )
        self.title = sw.CardTitle(children=[v.Spacer(), self.w_state])
        self.subtitle = v.CardSubtitle(children=[])
        self.content = v.CardText(children=[])

        self.children = [
            self.title,
            self.subtitle,
            v.Divider(),
            self.content,
        ]

    def update(self, sub):
        """Extract the info from the subscription and set it in the card"""

        title = sub["plan"]["name"].replace("_", " ")
        state = sub["state"].capitalize()
        self.w_state.values = sub["state"]

        from_ = datetime.fromisoformat(sub["active_from"])
        to = datetime.fromisoformat(sub["active_to"])
        now = datetime.now(timezone.utc)
        days_left = (to - now).days

        info_dict = {
            "from": ["From:", from_.strftime("%Y/%m/%d")],
            "to": ["Until:", to.strftime("%Y/%m/%d")],
            "days_left": ["Days left:", f"{days_left}"],
        }

        title_children = self.title.children
        if len(title_children) == 2:
            self.title.set_children(title)
        else:
            self.title.children = [title] + title_children[1:]

        self.subtitle.children = [state]

        content = [
            (
                v.Flex(
                    class_="d-block",
                    children=[
                        v.Html(tag="strong", children=[values[0]]),
                        v.Html(tag="div", children=[values[1]]),
                    ],
                ),
                v.Divider(vertical=True, class_="mx-4"),
            )
            for values in info_dict.values()
        ]
        # Flat the nested elements and remove the last divider
        content = [e for row in content for e in row][:-1]

        self.content.children = [v.Layout(class_="d-flex flex-wrap", children=content)]

        return self
