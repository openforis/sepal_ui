import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui import color
from sepal_ui.message import ms
from sepal_ui.planetapi import PlanetModel
from sepal_ui.scripts.decorator import loading_button


class PlanetView(sw.Layout):
    """Stand-alone interface to capture planet lab credentials, validate its  subscription and
    connect to the client stored in the model.

    Args:
        btn (sw.Btn, optional): Button to trigger the validation process in the associated model.
        alert (sw.Alert, v.Alert, optional): Alert component to display end-user action results.
        planet_model (sepal_ui.planetlab.PlanetModel): backend model to manipulate interface actions.

    """

    planet_model = None
    "sepal_ui.planetlab.PlanetModel: backend model to manipulate interface actions"

    btn = None
    "sw.Btn: Button to trigger the validation process in the associated model"

    alert = None
    "sw.Alert: Alert component to display end-user action results"

    w_username = None
    "sw.TextField: widget to set credential username"

    w_password = None
    "sw.PasswordField: widget to set credential password"

    w_key = None
    "sw.PasswordField: widget to set credential API key"

    w_state = None
    "sw.StateIcon: circle widget to inform the user on the current connection state"

    w_method = None
    "sw.Select: dropdown widget to select connection method"

    def __init__(self, *args, btn=None, alert=None, planet_model=None, **kwargs):

        self.class_ = "d-block flex-wrap"

        super().__init__(*args, **kwargs)

        self.planet_model = planet_model if planet_model else PlanetModel()
        self.btn = btn if btn else sw.Btn("Validate", small=True, class_="mr-1")
        self.alert = alert if alert else sw.Alert()

        self.w_username = sw.TextField(
            label=ms.planet.widget.username, class_="mr-2", v_model=""
        )
        self.w_password = sw.PasswordField(label=ms.planet.widget.password)
        self.w_key = sw.PasswordField(label=ms.planet.widget.apikey, v_model="").hide()

        states = {
            False: (ms.planet.status.offilne, color.error),
            True: (ms.planet.status.online, color.success),
        }

        self.w_state = sw.StateIcon(self.planet_model, "active", states)

        self.w_method = v.Select(
            label=ms.planet.widget.method.label,
            class_="mr-2",
            v_model="credentials",
            items=[
                {"value": "credentials", "text": ms.planet.widget.method.credentials},
                {"value": "api_key", "text": ms.planet.widget.method.api_key},
            ],
        )

        w_validation = v.Flex(
            style_="flex-grow: 0 !important;",
            children=[self.btn, self.w_state],
            class_="pr-1 flex-nowrap",
        )
        self.children = [
            self.w_method,
            sw.Layout(
                class_="align-center",
                children=[
                    self.w_username,
                    self.w_password,
                    self.w_key,
                ],
            ),
        ]

        if not btn:
            self.children[-1].set_children(w_validation, "last")

        if not alert:
            self.set_children(self.alert, "last")

        self.w_method.observe(self._swap_inputs, "v_model")
        self.btn.on_event("click", self.validate)

    def reset(self):
        """Empty credentials fields and restart activation mode"""

        self.w_username.v_model = None
        self.w_password.v_model = None
        self.w_key.v_model = None
        self.planet_model.active = False

        return

    def _swap_inputs(self, change):
        """Swap between credentials and api key inputs"""

        self.alert.reset()
        self.reset()

        self.w_username.toggle_viz()
        self.w_password.toggle_viz()
        self.w_key.toggle_viz()

        return

    @loading_button(debug=True)
    def validate(self, *args):
        """Initialize planet client and validate if is active"""

        if self.w_method.v_model == "credentials":
            credentials = [self.w_username.v_model, self.w_password.v_model]
        else:
            credentials = [self.w_key.v_model]

        self.planet_model.init_session(credentials)

        return
