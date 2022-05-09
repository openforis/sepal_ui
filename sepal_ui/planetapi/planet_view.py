import sepal_ui.scripts.utils as su
from traitlets import observe, dlink, Bool
from planet_model import PlanetModel
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw


class StateIcon(sw.Tooltip):

    valid = Bool(False).tag(sync=True)

    def __init__(self, model):

        self.right = True
        self.icon = v.Icon(children=["fas fa-circle"], color="red", small=True)

        super().__init__(self.icon, "Not connected")

        dlink((model, "active"), (self, "valid"))

    @observe("valid")
    def swap(self, change):
        """Swap between active and deactive mode"""

        if change["new"]:
            self.icon.color = "green"
            self.children = ["Connected"]
        else:
            self.icon.color = "red"
            self.children = ["Not connected"]


class PlanetView(sw.Layout):
    def __init__(self, *args, btn=None, alert=None, planet_model=None, **kwargs):
        """Stand-alone interface to capture planet lab credentials, validate its  subscription and
        connect to the client stored in the model.

        Args:
            bnt (sw.Btn, optional): Button to trigger the validation process in the associated model.
            alert (sw.Alert, v.Alert, optional): Alert component to display end-user action results.
            planet_model (sepal_ui.planetlab.PlanetModel): backend model to manipulate interface actions.

        """

        self.class_ = "d-block flex-wrap"

        super().__init__(*args, **kwargs)

        self.planet_model = planet_model if planet_model else PlanetModel()
        self.btn = btn if btn else sw.Btn("Validate", small=True, class_="mr-1")
        self.alert = alert if alert else sw.Alert()

        self.w_username = sw.TextField(
            label="Planet username", class_="mr-2", v_model=""
        )
        self.w_password = sw.PasswordField(label="Planet password")
        self.w_key = sw.PasswordField(label="Planet API key", v_model="").hide()
        self.w_state = StateIcon(self.planet_model)

        self.w_method = v.Select(
            label="Login method",
            class_="mr-2",
            v_model="credentials",
            items=[
                {"value": "api_key", "text": "API Key"},
                {"value": "credentials", "text": "Credentials"},
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

    def _swap_inputs(self, change):
        """Swap between credentials and api key inputs"""

        self.planet_model._init_client(None)
        self.alert.reset()

        if change["new"] == "api_key":
            self.w_username.hide()
            self.w_password.hide()
            self.w_key.show()
        else:
            self.w_username.show()
            self.w_password.show()
            self.w_key.hide()

    @su.loading_button()
    def validate(self, *args):
        """Initialize planet client and validate if is active"""

        if self.w_method.v_model == "credentials":
            credentials = (self.w_username.v_model, self.w_password.v_model)
        else:
            credentials = self.w_key.v_model

        self.planet_model._init_client(credentials, event=True)
