"""Widgets used to build the ``PLanetView`` interface."""

from datetime import datetime, timezone
from typing import List, Optional

import ipyvuetify as v
from typing_extensions import Self

import sepal_ui.sepalwidgets as sw
from sepal_ui.planetapi.planet_model import PlanetModel

# key_name: [label, [non_active_color, active_color]]
BTNS: dict = {
    "nicfi": ["NICFI", ["menu", "success"]],
    "others": ["Others", ["menu", "success"]],
}


class InfoView(sw.ExpansionPanels):

    model: Optional[PlanetModel] = None
    "Backend model to manipulate interface actions"

    def __init__(self, model: PlanetModel, **kwargs) -> None:
        """Card to validate subscription.

        Custom optinal card to be displayed within the planet view to validate the available
        subscriptions from the log-in credentials and show the info related with them, such
        as the quotas and remaining time of activation.

        Args:
            model: the planetModel associated with the display
        """
        self.model = model
        self.v_model = 1
        self.current = None
        self.readonly = True

        super().__init__(**kwargs)

        subs_btn = [
            sw.Chip(
                children=[BTNS[label][0]],
                disabled=True,
                color=BTNS[label][1][0],
                x_small=True,
                class_="mr-2",
                attributes={"id": label},
                link=True,
                label=True,
            )
            for label in BTNS.keys()
        ]

        self.info_card = InfoCard().hide()

        self.children = [
            v.ExpansionPanel(
                children=[
                    v.ExpansionPanelHeader(
                        hide_actions=True, children=[v.Flex(children=subs_btn)]
                    ),
                    v.ExpansionPanelContent(v_model=1, children=[self.info_card]),
                ]
            )
        ]

        [chip.on_event("click", self.open_info) for chip in subs_btn]

        self.model.observe(self._toggle_btns, "subscriptions")

    def open_info(self, widget: v.VuetifyWidget, *args) -> None:
        """Shrink or srhunk the content of the expansion panel.

        It automatically sends a request to build the data.

        Args:
            widget: the widget to expand
        """
        is_current = self.current == widget.attributes["id"]
        self.v_model = (not self.v_model) * 1 if is_current else 0
        self.current = widget.attributes["id"]

        subs_group = self.model.subscriptions[widget.attributes["id"]]

        self.info_card.update(subs_group).show()

        return

    def _turn_btn(self, btn_id: str, state: bool) -> None:
        """Update the status of the given button.

        Args:
            btn_id: the id of the btn object
            state: the state to apply to the btn
        """
        btn = self.get_children(attr="id", value=btn_id)[0]
        btn.disabled = not state
        btn.color = BTNS[btn_id][1][state]

        return

    def _toggle_btns(self, change: dict) -> None:
        """Toggle the status of the btns."""
        if not change["new"]:
            self.v_model = 1
            [self._turn_btn(btn_id, False) for btn_id in BTNS.keys()]
            return

        for plan_type in BTNS.keys():
            for subs in self.model.subscriptions[plan_type]:
                plan = subs.get("plan")
                # Turn on if at least one of them is True
                state = True if plan.get("state") else False
                self._turn_btn(plan_type, state)
                if state:
                    break

        return


class InfoCard(sw.Layout):
    def __init__(self) -> None:
        """Information card that will display the subscription data."""
        self.style_ = "max-height: 240px; overflow: auto"
        self.class_ = "d-block"

        super().__init__()

        self.children = [v.CardText(children=[])]

    def _make_content(self, sub: dict) -> List[v.VuetifyWidget]:
        """Creates individual subscription card from a subscription list.

        Args:
            sub: the subscriptions plan from a defined category (e.g. "nicfi")

        Returns:
            the children content of a category
        """
        title = sub["plan"]["name"].replace("_", " ")
        state = sub["plan"]["state"]

        # Create an individual State icon for all the elements, it has to be
        # independant
        w_state = sw.StateIcon(
            states={
                "non_active": ["Non active", "error"],
                "active": ["Active", "success"],
            }
        )
        w_state.values = state

        w_title = sw.CardTitle(children=[title, v.Spacer(), w_state])
        w_subtitle = v.CardSubtitle(children=[state.capitalize()])

        from_ = datetime.fromisoformat(sub["active_from"])
        to = sub["active_to"] is not None and datetime.fromisoformat(sub["active_to"])
        now = datetime.now(timezone.utc)
        days_left = "∞" if not to else (to - now).days

        info_dict = {
            "from": ["From:", from_.strftime("%Y/%m/%d")],
            "to": ["Until:", "∞" if not to else to.strftime("%Y/%m/%d")],
            "days_left": ["Days left:", f"{days_left}"],
        }

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

        return [
            w_title,
            w_subtitle,
            v.Layout(class_="d-flex flex-wrap", children=content),
            v.Divider(class_="my-2"),
        ]

    def update(self, subs_group: List[dict]) -> Self:
        """Extract the info from the subscription and set it in the card.

        Args:
            subs_group: list of subscriptions belonging to the same category ('nicfi', 'others')
        """
        content = [
            v.Card(class_="pa-2", children=self._make_content(sub))
            for sub in subs_group
        ]

        self.children = content

        return self
